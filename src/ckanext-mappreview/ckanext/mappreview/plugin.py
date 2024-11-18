import json
from urllib.parse import urlencode
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
    mappreview = get_mappreview(pkg)
    if not mappreview:
        return {}
    return json.loads(mappreview['value'])


def get_layer_js(layer, config):
    titiler_url = get_config()['titiler_url']
    query_params = {
        'colormap_name': 'viridis',
        'bidx': 1,
        'url': layer['url'],
        'rescale': f'{layer["pixel_percentile_2"]},{layer["pixel_percentile_98"]}',
    }
    layer_url = titiler_url + "/cog/tiles/WebMercatorQuad/{z}/{x}/{y}@2x?" + urlencode(query_params)
    return f"L.tileLayer('{layer_url}').addTo(map);"


def get_layers_js(pkg):
    layers = parse_metadata(pkg).get('layers') or []
    return '\n'.join([get_layer_js(layer, config) for layer in layers])


def generate_map_code(pkg):
    return """
<div id="map" style="width: 100%; height: 400px;"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
  var map = L.map('map').setView([0, 0], 4);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

""" + get_layers_js(pkg) + """
</script>
"""


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
            'mappreview_generate_map_code': generate_map_code,
        }
