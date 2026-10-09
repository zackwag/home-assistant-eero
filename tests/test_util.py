"""Tests for Eero utility functions."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eero.const import (
    CONF_BACKUP_NETWORKS,
    CONF_BACKUP_NETWORKS_INCLUDE_ALL,
    CONF_EEROS,
    CONF_EEROS_INCLUDE_ALL,
    CONF_FILTER_EXCLUDE,
    CONF_FILTER_INCLUDE,
    CONF_PROFILES,
    CONF_PROFILES_INCLUDE_ALL,
    CONF_WIRED_CLIENTS,
    CONF_WIRED_CLIENTS_FILTER,
    CONF_WIRELESS_CLIENTS,
    CONF_WIRELESS_CLIENTS_FILTER,
)
from custom_components.eero.util import (
    backup_network_allowed,
    client_allowed,
    eero_allowed,
    profile_allowed,
    resource_allowed,
)


def test_resource_allowed_include_all():
    """Test resource_allowed returns True when include_all is set."""
    resources = {CONF_EEROS_INCLUDE_ALL: True, CONF_EEROS: []}
    assert resource_allowed("any_id", resources, CONF_EEROS, CONF_EEROS_INCLUDE_ALL)


def test_resource_allowed_in_list():
    """Test resource_allowed returns True when resource is in the list."""
    resources = {CONF_EEROS: ["eero_1", "eero_2"]}
    assert resource_allowed("eero_1", resources, CONF_EEROS, CONF_EEROS_INCLUDE_ALL)


def test_resource_allowed_not_in_list():
    """Test resource_allowed returns False when resource is not in the list."""
    resources = {CONF_EEROS: ["eero_1"]}
    assert not resource_allowed("eero_2", resources, CONF_EEROS, CONF_EEROS_INCLUDE_ALL)


def test_eero_allowed():
    """Test eero_allowed helper."""
    resources = {CONF_EEROS: ["123"], CONF_EEROS_INCLUDE_ALL: False}
    assert eero_allowed("123", resources)
    assert not eero_allowed("456", resources)


def test_profile_allowed():
    """Test profile_allowed helper."""
    resources = {CONF_PROFILES: ["p1"], CONF_PROFILES_INCLUDE_ALL: False}
    assert profile_allowed("p1", resources)
    assert not profile_allowed("p2", resources)


def test_backup_network_allowed():
    """Test backup_network_allowed helper."""
    resources = {CONF_BACKUP_NETWORKS: ["bn1"], CONF_BACKUP_NETWORKS_INCLUDE_ALL: False}
    assert backup_network_allowed("bn1", resources)
    assert not backup_network_allowed("bn2", resources)


def test_client_allowed_wireless_include():
    """Test client_allowed with wireless include filter."""
    client = MagicMock()
    client.wireless = True
    client.id = "client_1"
    resources = {
        CONF_WIRELESS_CLIENTS_FILTER: CONF_FILTER_INCLUDE,
        CONF_WIRELESS_CLIENTS: ["client_1"],
        CONF_WIRED_CLIENTS_FILTER: CONF_FILTER_INCLUDE,
        CONF_WIRED_CLIENTS: [],
    }
    assert client_allowed(client, resources)
    client.id = "client_2"
    assert not client_allowed(client, resources)


def test_client_allowed_wireless_exclude():
    """Test client_allowed with wireless exclude filter."""
    client = MagicMock()
    client.wireless = True
    client.id = "client_1"
    resources = {
        CONF_WIRELESS_CLIENTS_FILTER: CONF_FILTER_EXCLUDE,
        CONF_WIRELESS_CLIENTS: ["client_1"],
        CONF_WIRED_CLIENTS_FILTER: CONF_FILTER_INCLUDE,
        CONF_WIRED_CLIENTS: [],
    }
    assert not client_allowed(client, resources)
    client.id = "client_2"
    assert client_allowed(client, resources)


def test_client_allowed_wired_include():
    """Test client_allowed with wired include filter."""
    client = MagicMock()
    client.wireless = False
    client.id = "client_1"
    resources = {
        CONF_WIRED_CLIENTS_FILTER: CONF_FILTER_INCLUDE,
        CONF_WIRED_CLIENTS: ["client_1"],
        CONF_WIRELESS_CLIENTS_FILTER: CONF_FILTER_INCLUDE,
        CONF_WIRELESS_CLIENTS: [],
    }
    assert client_allowed(client, resources)


def test_client_allowed_wired_exclude():
    """Test client_allowed with wired exclude filter."""
    client = MagicMock()
    client.wireless = False
    client.id = "client_1"
    resources = {
        CONF_WIRED_CLIENTS_FILTER: CONF_FILTER_EXCLUDE,
        CONF_WIRED_CLIENTS: ["client_1"],
        CONF_WIRELESS_CLIENTS_FILTER: CONF_FILTER_INCLUDE,
        CONF_WIRELESS_CLIENTS: [],
    }
    assert not client_allowed(client, resources)
