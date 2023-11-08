"""Tests for helpers.py."""

import ckanext.natcap.helpers as helpers


def test_natcap_hello():
    assert helpers.natcap_hello() == "Hello, natcap!"
