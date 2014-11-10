#!/usr/bin/env python
# ----------------------------------------------------------------------
#  Copyright (C) 2014 Numenta Inc. All rights reserved.
#
#  The information and source code contained herein is the
#  exclusive property of Numenta Inc. No part of this software
#  may be used, reproduced, stored or distributed in any form,
#  without explicit written authorization from Numenta Inc.
# ----------------------------------------------------------------------

""" This script calculates various metrics related to AWS hourly burn rate."""
import os
import boto
import boto.exception
from boto.ec2 import regions

#Prices last updated 6/12/14
#These are prices for On-Demand Instances
COST_MATRIX = {"us-east-1": {"m1.small":0.044,
                            "m1.medium":0.087,
                            "m1.large":0.175,
                            "m1.xlarge":0.350,
                            "m3.medium":0.070,
                            "m3.large":0.140,
                            "m3.xlarge":0.280,
                            "m3.2xlarge":0.560,
                            "cc2.8xlarge":2.00},
              "us-west-2": {"m1.small":0.047,
                            "m1.medium":0.095,
                            "m1.large":0.190,
                            "m1.xlarge":0.379,
                            "m3.medium":0.077,
                            "m3.large":0.154,
                            "m3.xlarge":0.308,
                            "m3.2xlarge":0.616,
                            "t1.micro":0.025} }



def getBurnRate(region, instance):
  if instance.state == "stopped":
    return 0.0
  #warning: If this function comes across an instance not in the dictionary, it will
  #         return a rate of $50.00/hr (much higher than any real hourly rate)
  #         which should be recognized by Grok as an anomaly. To fix just update
  #         the COST_MATRIX with the propper rates.
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

      regionalData.update({"%s" % r.name: {"burnrate":totalByRegion,
                                           "numberRunningInstances":numRunning,
                                           "numberStoppedInstances":numStopped,
                                           "numberAllInstances":numRunning+numStopped}})
    except boto.exception.EC2ResponseError:
      pass
  return regionalData
