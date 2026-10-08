"""The Eero integration."""

from __future__ import annotations

from .api.client import EeroClient
from .const import (
    CONF_FILTER_EXCLUDE,
    CONF_FILTER_INCLUDE,
    CONF_WIRED_CLIENTS,
    CONF_WIRED_CLIENTS_FILTER,
    CONF_WIRELESS_CLIENTS,
    CONF_WIRELESS_CLIENTS_FILTER,
)


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
