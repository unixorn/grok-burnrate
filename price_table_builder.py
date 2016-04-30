# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2016, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""
Output EC2 Instance pricing table to stdout as a JSON list. Each element in the
JSON list is a two-tuple, where the first value key consists
of (all lower-case): instance type, region, platform; the second value is
an object with key="USD" and value is the amount per hour in US$.

Example:  [["c1.medium", "ap-northeast-1", "rhel"], {"USD": 0.218}]

Reference https://aws.amazon.com/blogs/aws/new-aws-price-list-api/
"""

import argparse
import json
import sys
import urllib2



_DEFAULT_OFFERS_URL = ("https://pricing.us-east-1.amazonaws.com/"
                       "offers/v1.0/aws/AmazonEC2/current/index.json")

_REGION_NAME_TO_REGION = {
  "US East (N. Virginia)": "us-east-1",
  "US West (N. California)": "us-west-1",
  "US West (Oregon)": "us-west-2",
  "EU (Ireland)": "eu-west-1",
  "EU (Frankfurt)": "eu-central-1",
  "Asia Pacific (Tokyo)": "ap-northeast-1",
  "Asia Pacific (Seoul)": "ap-northeast-2",
  "Asia Pacific (Singapore)": "ap-southeast-1",
  "Asia Pacific (Sydney)": "ap-southeast-2",
  "South America (Sao Paulo)": "sa-east-1"
}



def buildLookupTable(offers):
  """Build lookup table of instance prices

  :param dict offers: AmazonEC2 offers formatted per
    https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json

  :returns: dict; each property's key consists of (all lower-case):
    instance type, region, platform; and the value is a dict with key="USD" and
    value is the amount per hour in US$. Example:
    {("c1.medium", "ap-northeast-1", "rhel"): {"USD": 0.218}, ...}
  """
  products = offers["products"]

  onDemandTerms = offers["terms"]["OnDemand"]

  priceMap = dict()

  for sku in products.itervalues():
    if sku.get("productFamily") != "Compute Instance":
      continue

    attributes = sku["attributes"]

    regionName = str(attributes["location"])

    if regionName == "AWS GovCloud (US)":
      continue

    instanceType = str(attributes["instanceType"])

    operatingSystem = str(attributes["operatingSystem"]).lower()

    skuId = sku["sku"]

    # Find pricing
    terms = onDemandTerms[skuId]

    if len(terms) != 1:
      raise Exception("Unexpected number of terms != 1: {}".format(terms))

    term = terms.values()[0]

    priceDimensions = term["priceDimensions"]

    if len(priceDimensions) != 1:
      raise Exception("Unexpected number of priceDimensions != 1: {}".format(
        priceDimensions))

    priceDimension = priceDimensions.values()[0]

    pricesPerUnit = priceDimension["pricePerUnit"]

    if len(pricesPerUnit) != 1:
      raise Exception(
        "Unexpected number of pricesPerUnit != 1 in rateCode={}: {}".format(
          priceDimension["rateCode"], pricesPerUnit))

    currency, amount = pricesPerUnit.items()[0]
    if currency != "USD":
      raise Exception("Unexpected currency {} in rateCode {}".format(
        currency, priceDimension["rateCode"]))

    key = (instanceType, _REGION_NAME_TO_REGION[regionName], operatingSystem)
    priceMap[key] = {
      "USD": float(amount)
    }


  return priceMap



def dump(fp, offersUrl=_DEFAULT_OFFERS_URL):
  """Download the offers table fromt he given URL, extract the instance pricing
  info and dump to a file in a format that may be retrieved with `load`

  :params file fp: file object for writing the instance pricing dump.
  :param str offersUrl: AmazonEC2 pricing offers URL, which may be an Internet "
    "URL (https://...) or an absolute file path (file:///...).
  """
  # Load the offers table
  response = urllib2.urlopen(offersUrl, timeout=300)
  offers = json.loads(response.read())

  # Convert map to list, because json can't handle our multi-item keys
  mapAsList = sorted(buildLookupTable(offers).iteritems())

  json.dump(mapAsList, fp, indent=4)



def load(fp):
  """Load the lookup table of instance prices from a file.

  :params file fp: file object for reading JSON dump created by this
    tool.

  :returns: dict; each property's key consists of (all lower-case):
    instance type, region, platform; and the value is a dict with key="USD" and
    value is the amount per hour in US$. Example:
    {("c1.medium", "ap-northeast-1", "rhel"): {"USD": 0.218}, ...}

  """
  return {
    tuple(key) : value for key, value in json.load(fp)
  }



def main():
  """Get AmazonEC2 offers URL from command-line options, load the offers table,
  parse it, and dump to stdout
  """
  parser = argparse.ArgumentParser(description=__doc__)

  parser.add_argument(
    "--url", type=str, required=False,
    default=_DEFAULT_OFFERS_URL,
    metavar="EC2_OFFERS_URL",
    dest="offersUrl",
    help="AmazonEC2 pricing offers URL, which may be an Internet URL "
    "(https://...) or an absolute file path (file:///...). Amazon's URL for "
    "retrieving the current AmazonEC2 offers is {}".format(_DEFAULT_OFFERS_URL))

  args = parser.parse_args()

  dump(sys.stdout, args.offersUrl)

  # Add a newline
  sys.stdout.write("\n")



if __name__ == "__main__":
  main()
