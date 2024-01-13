"""A script to take an MCF and upload it to CKAN.

If the dataset already exists, then its attributes are updated.

Dependencies:
    $ mamba install ckanapi pyyaml
"""
import os
import sys

import yaml
from ckanapi import RemoteCKAN

URL = "https://data.naturalcapitalproject.stanford.edu"


def main():
    mcf_file = yaml.load(sys.argv[1], Loader=yaml.Loader)

    catalog = RemoteCKAN(URL, apikey=os.environ['CKAN_APIKEY'])
    try:
        catalog.action.package_create(
        )
    except AttributeError:
        print(dir(catalog.action))



if __name__ == '__main__':
    main()
