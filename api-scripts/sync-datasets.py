#!/usr/bin/env python
import json
import os
import requests
import yaml

SRC = os.environ.get('SYNC_SRC_URL', 'https://data.naturalcapitalproject.stanford.edu')
DST = os.environ.get('SYNC_DST_URL', 'http://localhost:5000')
DST_APIKEY = os.environ['SYNC_DST_CKAN_APIKEY']
TITILER_URL = os.environ.get('TITILER_URL',
                             'https://titiler-897938321824.us-west1.run.app')


def get_dataset_metadata(dataset):
    if dataset['resources']:
        for resource in dataset['resources']:
            if resource['description'] == 'Geometamaker YML':
                r = requests.get(resource['url'])
                return yaml.safe_load(r.text)
    return None


def get_dataset_sources(dataset_metadata):
    return dataset_metadata.get('sources', None)


def get_raster_info(url):
    r = requests.get(TITILER_URL + '/cog/info', params={'url': url})
    j = r.json()
    return {
        'bounds': j['bounds'],
        'minzoom': j['minzoom'],
        'maxzoom': j['maxzoom'],
    }


def get_raster_statistics(url):
    statistics_response = requests.get(TITILER_URL + '/cog/statistics', params={'url': url})
    stats = statistics_response.json()['b1']
    return {
        'min': stats['min'],
        'max': stats['max'],
        'percentile_2': stats['percentile_2'],
        'percentile_98': stats['max'],
    }


def get_map_settings(layers):
    return {
        'minzoom': min([l['minzoom'] for l in layers]),
        'maxzoom': max([l['maxzoom'] for l in layers]),
        'bounds': [
            min([l['bounds'][0] for l in layers]),
            min([l['bounds'][1] for l in layers]),
            max([l['bounds'][2] for l in layers]),
            max([l['bounds'][3] for l in layers]),
        ],
    }

def get_mappreview_metadata(dataset):
    # TODO vectors
    raster_resources = [r for r in dataset['resources'] if r['format'] == 'GeoTIFF']
    layers = []

    for r in raster_resources:
        info = get_raster_info(r['url'])
        stats = get_raster_statistics(r['url'])

        layers.append({
            'name': r['name'],
            'type': 'raster',
            'url': r['url'],
            'pixel_min_value': stats['min'],
            'pixel_max_value': stats['max'],
            'pixel_percentile_2': stats['percentile_2'],
            'pixel_percentile_98': stats['percentile_98'],
            'bounds': info['bounds'],
            'minzoom': info['minzoom'],
            'maxzoom': info['maxzoom'],
        })

    if len(layers) > 0:
        return {
            'map': get_map_settings(layers),
            'layers': layers,
        }

    return None


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

        mappreview_metadata = get_mappreview_metadata(package)
        if mappreview_metadata:
            package['extras'].append({'key': 'mappreview', 'value': json.dumps(mappreview_metadata)})

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
