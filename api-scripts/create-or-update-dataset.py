"""A script to take an MCF and upload it to CKAN.

If the dataset already exists, then its attributes are updated.

Dependencies:
    $ mamba install ckanapi pyyaml
"""
import datetime
import difflib
import hashlib
import logging
import os
import pprint
import sys

import ckanapi.errors
import requests
import yaml
from ckanapi import RemoteCKAN

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(os.path.basename(__file__))

URL = "https://data.naturalcapitalproject.stanford.edu"

MODIFIED_APIKEY = os.environ['CKAN_APIKEY']


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


def _find_license(license_string, license_url, known_licenses):
    string_to_licenseid = {}
    url_to_licenseid = {}
    for license_id, license_data in known_licenses:
        url_to_licenseid[license_data['url']] = license_id
        string_to_licenseid[license_data['title']] = license_id
        if 'legacy_ids' in license_data:
            for legacy_id in license_data['legacy_ids']:
                string_to_licenseid[legacy_id] = license_id

    # TODO do a difflib comparison for similar strings if no match found

    if license_url:
        return url_to_licenseid[license_url]
    else:
        return string_to_licenseid[license_string]


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
    current_mcf_value = mcf
    for key in dot_keys.split('.'):
        try:
            current_mcf_value = current_mcf_value[key]
            if not isinstance(current_mcf_value, dict):
                return current_mcf_value
        except KeyError:
            break
    LOGGER.warning(f"MCF does not contain {dot_keys}: {key} not found")
    return ''


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

        # does the package already exist?

        try:
            title = mcf['identification']['title']
            name = title.lower().replace(' ', '_')

            # check if the package exists
            try:
                LOGGER.info(
                    f"Checking to see if package exists with name={name}")
                pkg_dict = catalog.action.package_show(name_or_id=name)
                LOGGER.info(f"Package already exists name={name}")
            except ckanapi.errors.NotFound:
                LOGGER.info(
                    f"Package not found; creating package with name={name}")

                # keys into the first contact info listing
                possible_author_keys = [
                    'individualname',
                    'organization',
                ]
                first_contact_info = list(mcf['contact'].values())[0]
                for author_key in possible_author_keys:
                    if first_contact_info[author_key]:
                        break  # just keep author_key

                pkg_dict = catalog.action.package_create(
                    name=name,
                    title=title,
                    private=False,
                    author=first_contact_info[author_key],
                    author_email=first_contact_info['email'],
                    owner_org='natcap',
                    notes=_get_from_mcf(mcf, 'identification.abstract'),
                    groups=[],
                )
            pprint.pprint(pkg_dict)

            # Resources:
            #   * The file we're referring to (at a different URL)
            #   * The ISO XML
            #   * The MCF file

            attached_resources = pkg_dict['resources']

            # if there are no resources, attach the MCF as a resource.
            if not attached_resources:
                LOGGER.info(f"Creating resource for {sys.argv[1]}")
                catalog.action.resource_create(
                    # URL parameter is not required by CKAN >=2.6
                    package_id=pkg_dict['id'],
                    description="Metadata Control File for this dataset",
                    format="YML",
                    hash=f"sha256:{_hash_file_sha256(sys.argv[1])}",
                    name=os.path.basename(sys.argv[1]),
                    #resource_type=  # not clear what this should be
                    mimetype='application/yaml',
                    #mimetype_inner  # what is this??
                    size=os.path.getsize(sys.argv[1]),
                    # Assuming "created" is when the metadata was created on ckan,
                    # but we should decide that officially.
                    #TODO: what should "created" date represent?
                    created=datetime.datetime.now().isoformat(),
                    last_modified=datetime.datetime.now().isoformat(),
                    cache_last_updated=datetime.datetime.now().isoformat(),
                    upload=open(sys.argv[1], 'rb')
                )

        except AttributeError:
            print(dir(catalog.action))


if __name__ == '__main__':
    main()
