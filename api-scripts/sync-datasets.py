#!/usr/bin/env python
import json
import os
import requests
import yaml

SRC = os.environ.get('SYNC_SRC_URL', 'https://data.naturalcapitalproject.stanford.edu')
DST = os.environ.get('SYNC_DST_URL', 'http://localhost:5000')
DST_APIKEY = os.environ['SYNC_DST_CKAN_APIKEY']


def get_dataset_metadata(dataset):
    if dataset['resources']:
        for resource in dataset['resources']:
            if resource['description'] == 'Geometamaker YML':
                r = requests.get(resource['url'])
                return yaml.safe_load(r.text)
    return None


def get_dataset_sources(dataset_metadata):
    return dataset_metadata.get('sources', None)


def delete_datasets(dst, dst_apikey):
    list_response = requests.get(dst + '/api/3/action/package_list')

    for id in list_response.json()['result']:
        print('Deleting ' + id)
        delete_response = requests.post(dst + '/api/action/package_delete',
                                        json={'id': id},
                                        headers={'Authorization': dst_apikey})
        purge_response = requests.post(dst + '/api/action/dataset_purge',
                                        json={'id': id},
                                        headers={'Authorization': dst_apikey})


def sync_datasets(src, dst, dst_apikey):
    list_response = requests.get(src + '/api/3/action/package_list')

    for id in list_response.json()['result']:
        print('Adding ' + id)
        package_response = requests.get(src + '/api/3/action/package_show?id=' + id)

        organization_id = None
        organization_response = requests.get(dst + '/api/action/organization_show?id=' + package_response.json()['result']['owner_org'])

        if organization_response.status_code == 404:
            print('Creating org')
            organization_post_response = requests.post(
                dst + '/api/action/organization_create',
                headers={'Authorization': dst_apikey},
                json=package_response.json()['result']['organization']
            )
            organization_id = organization_post_response.json()['result']['id']

        package = package_response.json()['result']
        package['extras'] = [] # XXX skipping extras for now

        # If dataset has metadata with sources in it, add those
        metadata = get_dataset_metadata(package)
        sources = get_dataset_sources(metadata)
        if sources:
            # TODO maybe better on the resource itself?
            package['extras'].append({'key': 'sources', 'value': json.dumps(sources)})

        post_response = requests.post(
            dst + '/api/action/package_create',
            headers={'Authorization': dst_apikey},
            json=package
        )

        if (post_response.status_code != 200):
            print(post_response.json()['error'])
            break


if __name__ == '__main__':
    print('Deleting existing datasets...')
    delete_datasets(DST, DST_APIKEY)
    print('Done.')

    print('Syncing datasets...')
    sync_datasets(SRC, DST, DST_APIKEY)
    print('Done.')
