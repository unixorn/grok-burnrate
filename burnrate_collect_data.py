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

""" Grok Custom Metrics data collector for collecting AWS burn rate metrics."""
import datetime, time, sys, csv, os.path
from optparse import OptionParser
from grokcli.api import GrokSession

from calculate_burn_rate import getDataByRegions



def sendMetricsToGrok(opt):
  """Collects data for burnrate metrics, writes it to a csv file and
  sends it to Grok.

  Collects the following metrics (toggled with CL flags):
  - Total hourly burnrate
  - Regional hourly burnrate (use -b)
  - Total number running instances
  - Regional number running instances (use -r)
  - Total number stopped instances
  - Regional number stopped instances (use -p)
  - Total number all instances
  - Regional number all instances (use -t)
  """
  grok = GrokSession(server=opt.server, apikey=opt.key)
  regionalData = getDataByRegions()
  ts = time.mktime(datetime.datetime.utcnow().timetuple())

  with open(opt.outputfile, "ab") as csvfile:
    csvwriter = csv.writer(csvfile)

    with grok.connect() as sock:
      # Regional burn rate calculation/send
      if opt.regionalBurnrates:
        if opt.verbose:
          print "Calculating / sending regional hourly burn rates"
        for region in regionalData.items():
          sock.sendall("%s %s %d\n" % (opt.prefix + "." + region[0] +
                                       ".burnrate",
                                       (region[1]["burnrate"]*int(opt.scale)),
                                       ts))
          csvwriter.writerow([(opt.prefix + "." + region[0] + ".burnrate"),
                              str(region[1]["burnrate"]),
                              str(ts)])

      # Total burn rate calculation/send
      if opt.verbose:
        print "Calculating / sending total hourly burn rate"
      burnrate = sum(region[1]["burnrate"] for region in regionalData.items())
      sock.sendall("%s %s %d\n" % (opt.prefix + ".total.burnrate",
                                   (burnrate*int(opt.scale)),
                                   ts))
      csvwriter.writerow([opt.prefix + ".total.burnrate",
                          str(burnrate),
                          str(ts)])

      # Regional running instances calculate/send
      if opt.regionalRunning:
        if opt.verbose:
          print "Calculating / sending regional running instances"
        for region in regionalData.items():
          sock.sendall("%s %s %d\n" % (opt.prefix + "." + region[0] +
                                       ".runningInstances",
                                       (region[1]["numberRunningInstances"]
                                        *int(opt.scale)),
                                       ts))
          csvwriter.writerow([(opt.prefix + "." + region[0] +
                               ".runningInstances"),
                              str(region[1]["numberRunningInstances"]),
                              str(ts)])
      # Total running instances calculate/send
      if opt.verbose:
        print "Calculating / sending total running instances"
      numRunning = sum(region[1]["numberRunningInstances"] for region in
                     regionalData.items())
      sock.sendall("%s %s %d\n" % (opt.prefix + ".total.runningInstances",
                                   (numRunning*int(opt.scale)),
                                   ts))
      csvwriter.writerow([opt.prefix + ".total.runningInstances",
                          str(numRunning),
                          str(ts)])

      # Regional stopped instances calculate/send
      if opt.regionalStopped:
        if opt.verbose:
          print "Calculating / sending regional stopped instances"
        for region in regionalData.items():
          sock.sendall("%s %s %d\n" % (opt.prefix + "." + region[0] +
                                       ".stoppedInstances",
                                       (region[1]["numberStoppedInstances"]
                                        *int(opt.scale)),
                                       ts))
          csvwriter.writerow([(opt.prefix + "." + region[0] +
                               ".stoppedInstances"),
                              str(region[1]["numberStoppedInstances"]),
                              str(ts)])

      # Total stopped instances calculate/send
      if opt.verbose:
        print "Calculating / sending total stopped instances"
      numStopped = sum(region[1]["numberStoppedInstances"] for region in
                     regionalData.items())
      sock.sendall("%s %s %d\n" % (opt.prefix + ".total.stoppedInstances",
                                   (numStopped*int(opt.scale)),
                                   ts))
      csvwriter.writerow([opt.prefix + ".total.stoppedInstances",
                          str(numStopped),
                          str(ts)])

      # Regional all instances calculate/send
      if opt.regionalAll:
        if opt.verbose:
          print "Calculating / sending regional all instances"
        for region in regionalData.items():
          sock.sendall("%s %s %d\n" % (opt.prefix + "." + region[0] +
                                       ".allInstances",
                                       (region[1]["numberAllInstances"]
                                        *int(opt.scale)),
                                       ts))
          csvwriter.writerow([(opt.prefix + "." + region[0] + ".AllInstances"),
                              str(region[1]["numberAllInstances"]),
                              str(ts)])

      # Total all instances calculate/send
      if opt.verbose:
        print "Calculating / sending total all instances"
      numAll = sum(region[1]["numberAllInstances"] for region in
                     regionalData.items())
      sock.sendall("%s %s %d\n" % (opt.prefix + ".total.allInstances",
                                   (numAll*int(opt.scale)),
                                   ts))
      csvwriter.writerow([opt.prefix + ".total.allInstances",
                          str(numAll),
                          str(ts)])


  if opt.verbose:
    print "Done!"


def writeMetricsToFile(opt):
  """Collects data for burnrate metrics and writes it to a csv file."""

  regionalData = getDataByRegions()
  ts = time.mktime(datetime.datetime.utcnow().timetuple())

  with open(opt.outputfile, "ab") as csvfile:
    csvwriter = csv.writer(csvfile)

    # Regional burn rate calculation/send
    if opt.regionalBurnrates:
      if opt.verbose:
        print "Calculating / writing regional hourly burn rates"
      for region in regionalData.items():
        csvwriter.writerow([(opt.prefix + "." + region[0] + ".burnrate"),
                            str(region[1]["burnrate"]),
                            str(ts)])

    # Total burn rate calculation/send
    if opt.verbose:
      print "Calculating / writing total hourly burn rate"
    burnrate = sum(region[1]["burnrate"] for region in regionalData.items())
    csvwriter.writerow([opt.prefix + ".total.burnrate",
                        str(burnrate),
                        str(ts)])

    # Regional running instances calculate/send
    if opt.regionalRunning:
      if opt.verbose:
        print "Calculating / writing regional running instances"
      for region in regionalData.items():
        csvwriter.writerow([(opt.prefix + "." + region[0] +
                             ".runningInstances"),
                            str(region[1]["numberRunningInstances"]),
                            str(ts)])
    # Total running instances calculate/send
    if opt.verbose:
      print "Calculating / writing total running instances"
    numRunning = sum(region[1]["numberRunningInstances"] for region in
                   regionalData.items())
    csvwriter.writerow([opt.prefix + ".total.runningInstances",
                        str(numRunning),
                        str(ts)])

    # Regional stopped instances calculate/send
    if opt.regionalStopped:
      if opt.verbose:
        print "Calculating / writing regional stopped instances"
      for region in regionalData.items():
        csvwriter.writerow([(opt.prefix + "." + region[0] +
                             ".stoppedInstances"),
                            str(region[1]["numberStoppedInstances"]),
                            str(ts)])

    # Total stopped instances calculate/send
    if opt.verbose:
      print "Calculating / writing total stopped instances"
    numStopped = sum(region[1]["numberStoppedInstances"] for region in
                   regionalData.items())
    csvwriter.writerow([opt.prefix + ".total.stoppedInstances",
                        str(numStopped),
                        str(ts)])

    # Regional total instances calculate/send
    if opt.regionalAll:
      if opt.verbose:
        print "Calculating / writing regional all instances"
      for region in regionalData.items():
        csvwriter.writerow([(opt.prefix + "." + region[0] +
                             ".allInstances"),
                            str(region[1]["numberAllInstances"]),
                            str(ts)])

    # Total total instances calculate/send
    if opt.verbose:
      print "Calculating / writing total all instances"
    numAll = sum(region[1]["numberAllInstances"] for region in
                   regionalData.items())
    csvwriter.writerow([opt.prefix + ".total.allInstances",
                        str(numAll),
                        str(ts)])

  if opt.verbose:
    print "Done!"


if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-s", "--server",
                    help="Grok server. (default: %default)",
                    dest="server", default="https://localhost")
  parser.add_option("-k", "--key",
                    help="Grok API key.",
                    dest="key", default="")
  parser.add_option("-i", "--inputfile",
                    help="File with existing burnrate data.",
                    dest="inputfile", default="")
  parser.add_option("-o", "--outputfile",
                    help="File to output data to. (default: %default)",
                    dest="outputfile", default="burnrates.csv")
  parser.add_option("-v", "--verbose",
                    help="Run in verbose mode. (default: %default)",
                    dest="verbose", action="store_true", default=False)
  parser.add_option("-n", "--noserver",
                    help="Don't send to server. (default: %default)",
                    dest="noserver", action="store_true", default=False)
  parser.add_option("-b",
                    help="Calculate burnrates by region.",
                    dest="regionalBurnrates", action="store_true", default=False)
  parser.add_option("-r",
                    help="Count running instances by region.",
                    dest="regionalRunning", action="store_true", default=False)
  parser.add_option("-p",
                    help="Count stopped instances by region.",
                    dest="regionalStopped", action="store_true", default=False)
  parser.add_option("-t",
                    help="Count total instances by region.",
                    dest="regionalAll", action="store_true", default=False)
  parser.add_option("--prefix",
                    help="Prefix for burnrate metrics. (default: %default)",
                    dest="prefix", default="aws")
  parser.add_option("--scale",
                    help="Scale metrics by this integer. (default: %default)",
                    dest="scale", default=1)


  opt, arg = parser.parse_args(sys.argv[1:])

  path = os.path.dirname(os.path.abspath(__file__))

  if ((opt.server=="" or opt.key=="") and not opt.noserver):
    print ("burnrate_collect_data.py -s <server> -k <key>")
    sys.exit(2)

  if opt.inputfile != "" and not opt.noserver:
    if opt.verbose:
      print "Sending existing data to grok..."
    with open(opt.inputfile, "rb") as inputFile:
      grok = GrokSession(server=opt.server, apikey=opt.key)
      with grok.connect() as sock:
        csvreader = csv.reader(inputFile)
        for row in csvreader:
          metricName = row[0]
          data = float(row[1])
          ts = row[2]
          sock.sendall("%s %s %s\n" % (metricName, (data*int(opt.scale)),
                                       int(float(ts))))
  else:
    if not os.path.isfile(opt.outputfile):
      open(opt.outputfile, "w").close()

    if not opt.noserver:
      sendMetricsToGrok(opt)
    else:
      writeMetricsToFile(opt)
