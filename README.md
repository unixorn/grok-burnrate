# AWS EC2 Burnrate Monitor for Grok Custom Metrics

This script is designed to send the burnrate statistics of an AWS account to
Grok as a custom metric. The burnrate metrics are useful for monitoring
anomalous spend rates on AWS based on actual burnrate and number of instances. 

This tool calculates the following metrics on an AWS account's EC2 instances: 
- Total burnrate
- Burnrate by region
- Total number of running instances
- Number of running instances by region
- Total number of stopped instances
- Number of stopped instances by region
- Total number of all instance types
- Number of all instance types by region

## What the script does do:

* Assumes stopped instances have no cost associated with them
* Assumes that all instances that are currently running will run for at least 1 more hour
* Counts all the instances of each type, then multiplies them by the base Amazon cost per hour per instance.

## What the script does _not_ do:

* Calculate any bandwidth charges.
* Calculate the cost of any EBS volumes you've attached to your instances.
* Calculate the cost of any snapshots of your instances.
* Deal with cost differences for reserved or spot instances.
* Figure out how much time is left before the currently running instances finish their current hour.
* Take into account what OS you're running. It assumes all your instances are generic Linux instances.
* Automatically update AWS pricing. The script currently uses the prices available as of 14-November-2014.

## Setup

### Manual setup:
The burnrate script is written in Python and requires that you have boto and grokcli installed. You'll also need pip and git, which don't ship by default on Amazon Linux. You'll want a wrapper script to set up your environment before calling burnrate.

Your linux distribution may require you to install pip first. To install pip on CentOS 7, you'll need to install epel and python-pip first with `yum install epel-release -y && yum install -y python-pip`

1. Install git and pip with `sudo yum install -y git python26-pip`
2. Install boto and grokcli with `sudo pip install boto grokcli`
3. Clone the burnrate repo with `git clone git@github.com:NumentaCorp/grok-burnrate.git`
4. Test by running it manually with `grok-burnrate/burnrate_collect_data -brpt -s YOUR_GROK_SERVER -k YOUR_API_KEY --verbose -o /path/to/ouput.csv`

You should see the following output:
```
Calculating / sending regional hourly burn rates
Calculating / sending total hourly burn rate
Calculating / sending regional running instances
Calculating / sending total running instances
Calculating / sending regional stopped instances
Calculating / sending total stopped instances
Calculating / sending regional all instances
Calculating / sending total all instances
Done!
```

### Docker setup:
I've created a Dockerfile that has everything you need included. You can either build it yourself with `docker build -t burnrate .` inside your git clone of grok-burnrate, or you can use our public burnrate Docker image with `docker pull grok/burnrate`

## Usage

### Manual setup

The burnrate monitor runs best as a cronjob that runs every 5 minutes. The
following examples show the various use cases of the burnrate monitor. 

#### Run burnrates from scratch with no previous data:

This example records all possible metrics (see options).

**Crontab entry:**
`*/5 * * * * ~/bin/burnrates.sh | logger -t burnrates`

**burnrates.sh:**
```
#!/bin/bash

export AWS_ACCESS_KEY_ID={ACCESS_KEY}
export AWS_SECRET_ACCESS_KEY={SECRET}
GROK_SERVER="https://yourEC2instance.example.com"
GROK_KEY=abc123
  
/usr/local/bin/burnrate_collect_data.py -s ${GROK_SERVER} -k ${GROK_KEY} -brpt
```

Add `grok-burnrate/burnrate_collect_data -brpt -s YOUR_GROK_SERVER -k YOUR_API_KEY --verbose -o /path/to/file.csv` to cron on one of your servers. Run it every 5 minutes.

### Docker setup

You'll want to run our Docker images with your credentials. I recommend using a wrapper script - here's an example I've imaginatively named burn:

```bash
#!/bin/bash
#
# Burn - runs the burnrate docker container to update a Grok server with AWS
#        cost metrics.

AWS_ACCESS_KEY_ID="AK0XFEEDCAFEDEADBEEF"
AWS_SECRET_ACCESS_KEY="ABCDEFGHIJKLMNOPQRSTUVWXYZ/zyxwvutsrqpon"
CONTAINER_NAME="grok/burnrate"
GROK_API_KEY="AbcDE"
GROK_SERVER="https://demogrokserver.example.com"

mkdir -p /grok/metrics
cd /grok

docker run \
  --rm -i \
  -e GROK_SERVER=${GROK_SERVER} \
  -e GROK_API_KEY=${GROK_API_KEY} \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -v $(pwd)/metrics:/metrics \
  -t ${CONTAINER_NAME} \
  /usr/local/bin/burnrate-metric
 ```

 Run this script every five minutes from cron on your Docker host. As with the manual installation, you should see the following output when you test your container manually:

 ```
 Calculating / sending regional hourly burn rates
 Calculating / sending total hourly burn rate
 Calculating / sending regional running instances
 Calculating / sending total running instances
 Calculating / sending regional stopped instances
 Calculating / sending total stopped instances
 Calculating / sending regional all instances
 Calculating / sending total all instances
 Done!
 ```

Once everything is working, add /path/to/burn-script to your crontab and run it every five minutes.

**Import existing burnrates:**
`/usr/local/bin/burnrates/burnrate_collect_data.py -s https://example.com -k {grok-key} -i oldburnrates.csv`

burnrate_collect_data.py options
--------------------------------

Flag | Description | Default
---- | ----------- | -------
-s {SERVER}, --server={SERVER} | Specify the Grok server to send metrics to. | "https://localhost"
-k {KEY}, --key={KEY} | Specify the Grok API key for the server. | None
-i {file}, --inputfile={file} | Specify the .csv file to pull backlogged data from. | None
-o {file}, --outputfile={file} | Specify the .csv file to record burnrate data to. | "burnrates.csv"
-v, --verbose | Enable verbose output mode. | False
-n, --noserver | Run the burnrate collector without a Grok server, only outputting metric data to outputfile. | False
--prefix | Prefix for burnrate metrics. | "aws"
--scale | Scale the sent data by an integer factor. | 1


### Regional flags

Flag | Description
---- | -----------
-b | Burnrates by region
-r | Nmber of running instances by region
-p | Number of stopped instances by region
-t | Number of all instance types by region
