"""Tests for views.py."""

import pytest

import ckanext.natcap.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "natcap")
@pytest.mark.usefixtures("with_plugins")
def test_natcap_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("natcap.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, natcap!"
