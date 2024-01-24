"""A script to take an MCF and upload it to CKAN.

If the dataset already exists, then its attributes are updated.

Dependencies:
    $ mamba install ckanapi pyyaml
"""
import logging
import os
import sys

import requests
import yaml
from ckanapi import RemoteCKAN

logging.basicConfig(level=logging.DEBUG)

URL = "https://data.naturalcapitalproject.stanford.edu"

MODIFIED_APIKEY = os.environ['CKAN_APIKEY']

def main():
    with open(sys.argv[1]) as yaml_file:
        mcf = yaml.load(yaml_file.read(), Loader=yaml.Loader)
    #import pdb; pdb.set_trace()

    session = requests.Session()
    session.headers.update({'Authorization': MODIFIED_APIKEY})

    #with RemoteCKAN(URL, apikey=os.environ['CKAN_APIKEY']) as catalog:
    with RemoteCKAN(URL, apikey=MODIFIED_APIKEY) as catalog:
        print('list org natcap', catalog.action.organization_list(id='natcap'))
        #import pdb; pdb.set_trace()
        #catalog.action.api_token_list(user_id='ff2c99c6-a004-4ade-b8b8-59030320eb4a')
        try:
            title = mcf['identification']['title']
            catalog.action.package_create(
                name=title.lower().replace(' ', '_'),
                title=title,
                private=False,
                owner_org='natcap',
                groups=[],
            )
        except AttributeError:
            print(dir(catalog.action))

        # TODO: upload ISO-rendered metadata object
        # TODO: upload MCF



if __name__ == '__main__':
    main()
