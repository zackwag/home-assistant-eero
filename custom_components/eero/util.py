"""The Eero integration."""

from __future__ import annotations

from .api.client import EeroClient
from .const import (
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


def resource_allowed(resource_id: str, resources: dict, conf_key: str, include_all_key: str) -> bool:
    """Check if a resource is allowed by configuration."""
    if resources.get(include_all_key, False):
        return True
    return resource_id in resources.get(conf_key, [])


def eero_allowed(eero_id: str, resources: dict) -> bool:
    """Check if an eero device is allowed."""
    return resource_allowed(eero_id, resources, CONF_EEROS, CONF_EEROS_INCLUDE_ALL)


def profile_allowed(profile_id: str, resources: dict) -> bool:
    """Check if a profile is allowed."""
    return resource_allowed(profile_id, resources, CONF_PROFILES, CONF_PROFILES_INCLUDE_ALL)


def backup_network_allowed(backup_network_id: str, resources: dict) -> bool:
    """Check if a backup network is allowed."""
    return resource_allowed(backup_network_id, resources, CONF_BACKUP_NETWORKS, CONF_BACKUP_NETWORKS_INCLUDE_ALL)


def client_allowed(client: EeroClient, resources: dict) -> bool:
    """Validate client against configuration."""
    if not client.wireless:
        if resources[CONF_WIRED_CLIENTS_FILTER] == CONF_FILTER_INCLUDE:
            return client.id in resources[CONF_WIRED_CLIENTS]
        if resources[CONF_WIRED_CLIENTS_FILTER] == CONF_FILTER_EXCLUDE:
            return client.id not in resources[CONF_WIRED_CLIENTS]
    else:
        if resources[CONF_WIRELESS_CLIENTS_FILTER] == CONF_FILTER_INCLUDE:
            return client.id in resources[CONF_WIRELESS_CLIENTS]
        if resources[CONF_WIRELESS_CLIENTS_FILTER] == CONF_FILTER_EXCLUDE:
            return client.id not in resources[CONF_WIRELESS_CLIENTS]
    return False
