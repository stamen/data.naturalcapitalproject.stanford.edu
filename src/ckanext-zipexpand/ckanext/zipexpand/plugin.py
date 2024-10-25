import json
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def parse_sources(sources):
    sources_arr = sorted(json.loads(sources))
    output_arr = []

    for s in sources_arr:
        components = s.split('\\')
        current_dir = None
        dir_options = output_arr

        for component in components[:-1]:
            current_dir = next((x for x in dir_options if x['name'] == component), None)
            if not current_dir:
                current_dir = { 'name': component, 'type': 'directory', 'children': [] }
                dir_options.append(current_dir)

            dir_options = current_dir['children']
            
        dir_options.append({
            'name': components[-1],
            'type': 'file',
            'extension': components[-1].split('.')[-1]
            })

    return output_arr


class ZipexpandPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "zipexpand")

    def get_helpers(self):
        return {'zipexpand_parse_sources': parse_sources}
