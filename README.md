AWS EC2 Burnrate Monitor for Grok Custom Metrics
================================================

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

Setup
-----
The burnrate scripts require grokcli and boto. Install them with
`pip install boto grokcli`

Your linux distribution may require you to install pip first. To install pip
on CentOS 7, you'll have to install epel and python-pip with
`yum install epel-release -y && yum install -y python-pip`

Usage
-----

The burnrate monitor runs best as a cronjob that runs every 5 minutes. The
following examples show the various use cases of the burnrate monitor. 

### Run burnrates from scratch with no previous data:

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
