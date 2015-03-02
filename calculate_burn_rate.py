#!/usr/bin/env python
#
# Copyright 2014-2015 Numenta Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

""" This script calculates various metrics related to AWS hourly burn rate."""
import os
import boto
import boto.exception
from boto.ec2 import regions

# Prices last updated 11/14/14
# These are the prices for On-Demand Instances
COST_MATRIX = {
                "us-east-1": {
                  "c1.medium": 0.13,
                  "c1.xlarge": 0.52,
                  "c3.large": 0.105,
                  "c3.xlarge": 0.21,
                  "c3.2xlarge": 0.42,
                  "c3.4xlarge": 0.84,
                  "c3.8xlarge": 1.68,
                  "cc2.8xlarge": 2.00,
                  "cg1.4xlarge": 2.1,
                  "cr1.8xlarge": 3.5,
                  "g2.2xlarge": 0.65,
                  "hi1.4xlarge": 3.1,
                  "hs1.8xlarge": 4.6,
                  "i2.xlarge": 0.853,
                  "i2.2xlarge": 1.705,
                  "i2.4xlarge": 3.41,
                  "i2.8xlarge": 6.82,
                  "m1.small": 0.044,
                  "m1.medium": 0.087,
                  "m1.large": 0.175,
                  "m1.xlarge": 0.350,
                  "m2.xlarge": 0.245,
                  "m2.2xlarge": 0.49,
                  "m2.4xlarge": 0.98,
                  "m3.medium": 0.07,
                  "m3.large": 0.14,
                  "m3.xlarge": 0.280,
                  "m3.2xlarge": 0.560,
                  "r3.large": 0.175,
                  "r3.xlarge": 0.35,
                  "r3.2xlarge": 0.7,
                  "r3.4xlarge": 1.4,
                  "r3.8xlarge": 2.8,
                  "t1.micro": 0.02,
                  "t2.micro": 0.013,
                  "t2.small": 0.026,
                  "t2.medium": 0.052,
                },
                "us-west-2": {
                  "c1.medium": 0.13,
                  "c1.xlarge": 0.52,
                  "cc2.8xlarge": 2.0,
                  "c3.large": 0.105,
                  "c3.xlarge": 0.21,
                  "c3.2xlarge": 0.42,
                  "c3.4xlarge": 0.84,
                  "c3.8xlarge": 1.68,
                  "cr1.8xlarge": 3.5,
                  "g2.2xlarge": 0.65,
                  "hs1.8xlarge": 4.6,
                  "h1.4xlarge": 3.1,
                  "i2.xlarge": 0.853,
                  "i2.2xlarge": 1.705,
                  "i2.4xlarge": 3.41,
                  "i2.8xlarge": 6.82,
                  "r3.large": 0.175,
                  "r2.xlarge": 0.35,
                  "r2.2xlarge": 0.7,
                  "r2.4xlarge": 1.4,
                  "r2.8xlarge": 2.8,
                  "m1.small": 0.044,
                  "m1.medium": 0.087,
                  "m1.large": 0.175,
                  "m1.xlarge": 0.35,
                  "m2.xlarge": 0.245,
                  "m2.2xlarge": 0.49,
                  "m2.4xlarge": 0.98,
                  "m3.medium": 0.07,
                  "m3.large": 0.14,
                  "m3.xlarge": 0.28,
                  "m3.2xlarge": 0.56,
                  "t1.micro": 0.02,
                  "t2.micro": 0.013,
                  "t2.small": 0.026,
                  "t2.medium": 0.052
                }
              }



def getBurnRate(region, instance):
  if instance.state == "stopped":
    return 0.0
  # Warning: If this function comes across an instance not in the dictionary,
  # it will return a rate of $50.00/hr (much higher than any real hourly rate)
  # which should be recognized by Grok as an anomaly. To fix just update the
  # COST_MATRIX with the propper rates.
  return COST_MATRIX.get(region.name, "us-west-2").get(instance.instance_type, 50.00)



def getDataByRegions():
  regionalData = {}
  for r in regions():
    try:
      conn = boto.connect_ec2(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region = r
      )
      reservations = conn.get_all_instances()
      totalByRegion = 0.0
      numStopped = 0
      numRunning = 0

      for reservation in reservations:
        for instance in reservation.instances:
          if instance.state == "stopped":
            numStopped += 1
          else:
            totalByRegion = totalByRegion + getBurnRate(r, instance)
            numRunning += 1

      regionalData.update({"%s" % r.name: {
                            "burnrate":totalByRegion,
                            "numberRunningInstances":numRunning,
                            "numberStoppedInstances":numStopped,
                            "numberAllInstances":numRunning+numStopped
                          }})
    except boto.exception.EC2ResponseError:
      pass
  return regionalData
