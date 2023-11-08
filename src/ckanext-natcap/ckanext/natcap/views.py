from flask import Blueprint


natcap = Blueprint(
    "natcap", __name__)


def page():
    return "Hello, natcap!"


natcap.add_url_rule(
    "/natcap/page", view_func=page)


def get_blueprints():
    return [natcap]
