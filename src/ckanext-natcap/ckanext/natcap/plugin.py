# encoding=utf-8
from __future__ import annotations

import json
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Schema


def get_resource_type_facet_label(resource_type_facet):
    return get_resource_type_label(resource_type_facet['name'])


def get_resource_type_label(resource_type):
    labels = {
        'csv': 'CSV',
        'geojson': 'GeoJSON',
        'tif': 'GeoTIFF',
        'shp': 'Shapefile',
        'txt': 'Text',
        'yml': 'YML',
    }
    return labels.get(resource_type, resource_type)


def parse_json(json_str):
    return json.loads(json_str)


class NatcapPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "natcap")

    def create_package_schema(self) -> Schema:
        # grab the default schema from core CKAN and update it.
        schema = super(NatcapPlugin, self).create_package_schema()
        schema.update({
            'suggested_citation': [toolkit.get_validator('ignore_missing'),
                                   toolkit.get_converter('convert_to_extras')],
        })
        return schema
    
    def update_package_schema(self) -> Schema:
        schema = super(NatcapPlugin, self).update_package_schema()
        schema.update({
            'suggested_citation': [toolkit.get_validator('ignore_missing'),
                                   toolkit.get_converter('convert_to_extras')],
        })
        return schema
    
    def show_package_schema(self) -> Schema:
        schema = super(NatcapPlugin, self).show_package_schema()
        schema.update({
            'suggested_citation': [toolkit.get_converter('convert_from_extras'),
                                   toolkit.get_validator('ignore_missing')],
        })
        return schema
    
    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self) -> list[str]:
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def get_helpers(self):
        return {
            'natcap_get_resource_type_facet_label': get_resource_type_facet_label,
            'natcap_get_resource_type_label': get_resource_type_label,
            'natcap_parse_json': parse_json,
        }

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['extras_placenames'] = toolkit._('Places')
        facets_dict['extras_sources_res_formats'] = toolkit._('Resource Formats')
        return facets_dict
