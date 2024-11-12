# encoding=utf-8
from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Schema


class NatcapPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)

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
