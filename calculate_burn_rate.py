#!/usr/bin/env python
#
# Copyright 2014-2016 Numenta Inc.
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

import shutil
import os
import sys
import tempfile
import time

import boto
import boto.exception
from boto.ec2 import regions

import price_table_builder



class _PriceTable(object):
  _CACHE_FILE_PATH = "/tmp/burnrate_instance_price_table.json"
  _MAX_CACHE_AGE_SEC = (24 * 3600)

  # Price table singleton in format returned by `price_table_builder.load()`
  _priceTableSingleton = None


  @classmethod
  def getTable(cls):
    """Return price table, possibly loading it from file and rebuilding cache
    if needed
    """
    if cls._priceTableSingleton is not None:
      return cls._priceTableSingleton

    needToRebuild = True

    # Check if cache needs to be rebuilt
    if os.path.exists(cls._CACHE_FILE_PATH):
      mtime = os.path.getmtime(cls._CACHE_FILE_PATH)
      if (time.time() - mtime) <= cls._MAX_CACHE_AGE_SEC:
        needToRebuild = False

    if needToRebuild:
      # Regnereate the pricing table

      # Create new pricing cache in temp file first, then move to static
      # location, to minimize window for corruption
      tempFd, tempPath = tempfile.mkstemp(
        suffix="burnrate_instance_price_table")

      with os.fdopen(tempFd, "wb") as fileObj:
        price_table_builder.dump(fileObj)

      shutil.move(tempPath, cls._CACHE_FILE_PATH)

      print >> sys.stderr, "(Re)built {}".format(cls._CACHE_FILE_PATH)

    # Load into memory
    with open(cls._CACHE_FILE_PATH) as inputFp:
      cls._priceTableSingleton = price_table_builder.load(inputFp)

    return cls._priceTableSingleton




def getBurnRate(instance):
  if instance.state == "stopped":
    return 0.0

  key = (instance.instance_type,
         instance.region.name,
         (instance.platform or "linux").lower())

  #warning: If this function comes across an instance not in the dictionary, it
  #         will return a rate of $50.00/hr (much higher than any real hourly
  #         rate) which should be recognized by Grok as an anomaly.
  return _PriceTable.getTable().get(key, {"USD": 50.00})["USD"]



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
            totalByRegion = totalByRegion + getBurnRate(instance)
            numRunning += 1

      regionalData.update(
        {"%s" % r.name: {"burnrate":totalByRegion,
                         "numberRunningInstances":numRunning,
                         "numberStoppedInstances":numStopped,
                         "numberAllInstances":numRunning+numStopped}})
    except boto.exception.EC2ResponseError:
      pass
  return regionalData
