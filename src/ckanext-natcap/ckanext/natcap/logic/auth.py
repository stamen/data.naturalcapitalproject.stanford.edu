import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def natcap_get_sum(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "natcap_get_sum": natcap_get_sum,
    }
