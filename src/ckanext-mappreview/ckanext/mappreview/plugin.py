import json
from ckan.common import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def get_config():
    namespace = 'ckanext.mappreview.'
    return dict([(k.replace(namespace, ''), v) for k, v in config.items() if k.startswith(namespace)])


def get_mappreview(pkg):
    return next((x for x in pkg['extras'] if x['key'] == 'mappreview'), None)


def should_show(pkg):
    return get_mappreview(pkg)


def parse_metadata(pkg):
    return json.loads(get_mappreview(pkg)['value'])


class MappreviewPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "mappreview")

    def get_helpers(self):
        return {
            'mappreview_get_config': get_config,
            'mappreview_parse_metadata': parse_metadata,
            'mappreview_should_show': should_show,
        }
