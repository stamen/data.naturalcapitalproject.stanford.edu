#!/usr/bin/env python
import json
import requests

DST_APIKEY = 'APIKEY'
SRC = 'https://data.naturalcapitalproject.stanford.edu'
DST = "http://localhost:5000"

list_response = requests.get(SRC + '/api/3/action/package_list')

for id in list_response.json()['result']:
    print(id)
    package_response = requests.get(SRC + '/api/3/action/package_show?id=' + id)

    organization_id = None
    organization_response = requests.get(DST + '/api/action/organization_show?id=' + package_response.json()['result']['owner_org'])
    print(organization_response.json()['result'])

    if organization_response.status_code == 404:
        print('Creating org')
        organization_post_response = requests.post(
            DST + '/api/action/organization_create',
            headers={'Authorization': DST_APIKEY},
            json=package_response.json()['result']['organization']
        )
        organization_id = organization_post_response.json()['result']['id']

    package = package_response.json()['result']
    package['extras'] = [] # XXX skipping extras for now

    post_response = requests.post(
        DST + '/api/action/package_create',
        headers={'Authorization': DST_APIKEY},
        json=package
    )

    print(post_response.status_code)
    if (post_response.status_code != 200):
        print(post_response.json()['error'])
        break

    print(post_response.text)
