import json
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


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
            'mappreview_parse_metadata': parse_metadata,
            'mappreview_should_show': should_show,
        }
