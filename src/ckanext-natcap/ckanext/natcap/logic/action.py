import ckan.plugins.toolkit as tk
import ckanext.natcap.logic.schema as schema


@tk.side_effect_free
def natcap_get_sum(context, data_dict):
    tk.check_access(
        "natcap_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.natcap_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


def get_actions():
    return {
        'natcap_get_sum': natcap_get_sum,
    }
