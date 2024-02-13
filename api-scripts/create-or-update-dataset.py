"""A script to take an MCF and upload it to CKAN.

If the dataset already exists, then its attributes are updated.

Dependencies:
    $ mamba install ckanapi pyyaml google-cloud-storage requests

Note:
    You will need to authenticate with the google cloud api in order to do
    anything with assets located on GCP.  To do this, install the google cloud
    SDK (https://cloud.google.com/sdk/docs/install) and then run this command
    at your shell:

        $ gcloud auth application-default login
"""
import collections
import datetime
import hashlib
import json
import logging
import mimetypes
import os
import pprint
import sys

import ckanapi.errors
import requests  # mamba install requests
import yaml  # mamba install pyyaml
from ckanapi import RemoteCKAN  # mamba install ckanapi
from google.cloud import storage  # mamba install google-cloud-storage

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(os.path.basename(__file__))

URL = "https://data.naturalcapitalproject.stanford.edu"

MODIFIED_APIKEY = os.environ['CKAN_APIKEY']

# Add a few mimetypes for extensions we're likely to encounter
for extension, mimetype in [
        ('.shp', 'application/octet-stream'),
        ('.dbf', 'application/dbase'),
        ('.shx', 'application/octet-stream'),
        ('.geojson', 'application/json')]:
    mimetypes.add_type(mimetype, extension)


def _hash_file_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(2**16)  # read in 64k at a time
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def _get_created_date(filepath):
    return datetime.datetime.utcfromtimestamp(
        os.path.getctime(filepath))


def _create_resource_dict_from_file(
        filepath, description, upload=False):
    now = datetime.datetime.now().isoformat()
    resource = {
        'description': description,
        # strip out the `.` from the extension
        'format': os.path.splitext(filepath)[1][1:].upper(),
        'hash': f"sha256:{_hash_file_sha256(filepath)}",
        'name': os.path.basename(filepath),
        'size': os.path.getsize(filepath),
        'created': now,
        'cache_last_updated': now,
    }

    print(filepath)
    mimetype, _ = mimetypes.guess_type(filepath)
    if mimetype:  # will be None if mimetype unknown
        resource['mimetype'] = mimetype

    if upload:
        resource['upload'] = open(filepath, 'rb')
    return resource


def _create_resource_dict_from_url(url, description):
    now = datetime.datetime.now().isoformat()

    if url.startswith('https://storage.cloud.google.com'):
        domain, bucket_name, key = url[8:].split('/', maxsplit=2)

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.get_blob(key)

        checksum = f"crc32c:{blob.crc32c}"
        size = blob.size
    else:
        raise NotImplementedError(
            f"Don't know how to check url for metadata: {url}")

    resource = {
        'url': url,
        'description': description,
        'format': os.path.splitext(url)[1][1:].upper(),
        'hash': checksum,
        'name': os.path.basename(url),
        'size': size,
        'created': now,
        'cache_last_updated': now,
    }
    mimetype, _ = mimetypes.guess_type(url)
    if mimetype:  # will be None if mimetype unknown
        resource['mimetype'] = mimetype
    return resource


def _find_license(license_string, license_url, known_licenses):

    # CKAN license IDs use:
    #   - dashes instead of spaces
    #   - all caps
    sanitized_license_string = license_string.strip().replace(
        ' ', '-').upper()

    # CKAN license URLs are expected to have a trailing backslash
    if not license_url.endswith('/'):
        license_url = f'{license_url}/'

    string_to_licenseid = {}
    url_to_licenseid = {}
    for license_data in known_licenses:
        license_id = license_data['id']
        url_to_licenseid[license_data['url']] = license_id
        string_to_licenseid[license_data['title']] = license_id
        if 'legacy_ids' in license_data:
            for legacy_id in license_data['legacy_ids']:
                string_to_licenseid[legacy_id] = license_id

    # TODO do a difflib comparison for similar strings if no match found

    if license_url:
        try:
            return url_to_licenseid[license_url]
        except KeyError:
            raise ValueError(f"License URL {license_url} not recognized")
    else:
        try:
            return string_to_licenseid[sanitized_license_string]
        except KeyError:
            raise ValueError(
                f"License {license_string} / {sanitized_license_string} not "
                "recognized")


def _get_from_mcf(mcf, dot_keys):
    """Retrieve an attribute from an MCF.

    If the attribute is not defined, an empty string is returned.

    Args:
        mcf (dict): The full MCF dictionary
        dot_keys (str): A dot-separated sequence of keys to sequentially index
            into the MCF.  For example: ``identification.abstract``

    Returns:
        value: The value of the attribute at the specified depth, or the empty
        string if the attribute indicated by ``dot_keys`` is not found.
    """
    print("looking for", dot_keys)
    current_mcf_value = mcf
    mcf_keys = collections.deque(dot_keys.split('.'))
    while True:
        key = mcf_keys.popleft()
        try:
            current_mcf_value = current_mcf_value[key]
            if not mcf_keys:  # we're at the root node
                return current_mcf_value
        except KeyError:
            break
    LOGGER.warning(f"MCF does not contain {dot_keys}: {key} not found")
    return ''


def _create_tags_dicts(mcf):
    tags_list = _get_from_mcf(mcf, 'identification.keywords.default.keywords')
    return [{'name': name} for name in tags_list]


def _get_wgs84_bbox(mcf):
    extent = _get_from_mcf(mcf, 'identification.extents.spatial')[0]
    assert int(extent['crs']) == 4326, 'CRS must be EPSG:4326'

    minx, miny, maxx, maxy = extent['bbox']

    return [[[minx, maxy], [minx, miny], [maxx, miny], [maxx, maxy],
             [minx, maxy]]]


def main():
    with open(sys.argv[1]) as yaml_file:
        LOGGER.debug(f"Loading MCF from {sys.argv[1]}")
        mcf = yaml.load(yaml_file.read(), Loader=yaml.Loader)

    session = requests.Session()
    session.headers.update({'Authorization': MODIFIED_APIKEY})

    with RemoteCKAN(URL, apikey=MODIFIED_APIKEY) as catalog:
        print('list org natcap', catalog.action.organization_list(id='natcap'))

        # TODO: can we force CKAN to refresh the license list?
        # It's still using the old 15-license list, not the full list.
        licenses = catalog.action.license_list()
        print(f"{len(licenses)} licenses found")

        license_id = ''
        if _get_from_mcf(mcf, 'identification.license'):
            license_id = _find_license(
                _get_from_mcf(mcf, 'identification.license.name'),
                _get_from_mcf(mcf, 'identification.license.url'),
                licenses)

        # does the package already exist?

        title = _get_from_mcf(mcf, 'identification.title')
        name = _get_from_mcf(mcf, 'metadata.identifier')

        # keys into the first contact info listing
        possible_author_keys = [
            'individualname',
            'organization',
        ]
        first_contact_info = list(mcf['contact'].values())[0]
        for author_key in possible_author_keys:
            if first_contact_info[author_key]:
                break  # just keep author_key

        resources = [
            _create_resource_dict_from_file(
                sys.argv[1], (
                    'Metadata Control File for this dataset, describing '
                    'metadata in a YML file format.'), upload=True),
        ]
        for distribution in _get_from_mcf(mcf, 'distribution').values():
            if distribution['function'].lower() == 'download':
                resources.append(
                    _create_resource_dict_from_url(
                        distribution['url'], distribution['description']))

        package_parameters = {
            'name': name,
            'title': title,
            'private': False,
            'author': first_contact_info[author_key],
            'author_email': first_contact_info['email'],
            'owner_org': 'natcap',
            'notes': _get_from_mcf(mcf, 'identification.abstract'),
            #'url': _get_from_mcf(mcf, 'identification.url'),
            'version': _get_from_mcf(mcf, 'identification.edition'),
            'license_id': license_id,
            'groups': [],

            # Just use existing tags as CKAN "free" tags
            # TODO: support defined vocabularies
            'tags': _create_tags_dicts(mcf),

            # We can define the bbox as a polygon using
            # ckanext-spatial's spatial extra
            'extras': [{
                'key': 'spatial',
                'value': json.dumps({
                    'type': 'Polygon',
                    'coordinates': _get_wgs84_bbox(mcf),
                }),
            }],
        }
        try:
            try:
                LOGGER.info(
                    f"Checking to see if package exists with name={name}")
                pkg_dict = catalog.action.package_show(name_or_id=name)
                LOGGER.info(f"Package already exists name={name}")
                pkg_dict = catalog.action.package_update(
                    id=pkg_dict['id'],
                    **package_parameters
                )
            except ckanapi.errors.NotFound:
                LOGGER.info(
                    f"Package not found; creating package with name={name}")
                pkg_dict = catalog.action.package_create(
                    **package_parameters
                )
            pprint.pprint(pkg_dict)

            # Resources:
            #   * The file we're referring to (at a different URL)
            #   * The ISO XML
            #   * The MCF file

            attached_resources = pkg_dict['resources']
            assert not attached_resources
            for resource in resources:
                catalog.action.resource_create(
                    package_id=pkg_dict['id'],
                    **resource
                )

        except AttributeError:
            print(dir(catalog.action))


if __name__ == '__main__':
    main()
