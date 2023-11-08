"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.natcap.logic import validators


def test_natcap_reauired_with_valid_value():
    assert validators.natcap_required("value") == "value"


def test_natcap_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.natcap_required(None)
