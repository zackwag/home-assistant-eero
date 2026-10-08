"""Eero API."""

from __future__ import annotations

from .const import URL_ACCOUNT


class EeroResource:
    """EeroResource."""

    _resource_type: str = "resource"

    def __init__(self, api, network, data) -> None:
        """Initialize."""
        self.api = api
        self.network = network
        self.data = data

    @property
    def id(self) -> str | None:
        """ID."""
        if self.is_network:
            return self.url.replace("/2.2/networks/", "")
        if self.is_eero:
            return self.url.replace("/2.2/eeros/", "")
        if self.is_profile:
            return self.url.replace(f"{self.network.url}/profiles/", "")
        if self.is_client:
            return self.url.replace(f"{self.network.url}/devices/", "")
        return None

    @property
    def is_account(self) -> bool:
        """Is account."""
        return self._resource_type == "account"

    @property
    def is_backup_network(self) -> bool:
        """Is backup network."""
        return self._resource_type == "backup_network"

    @property
    def is_client(self) -> bool:
        """Is client."""
        return self._resource_type == "client"

    @property
    def is_eero(self) -> bool:
        """Is Eero."""
        return self._resource_type in ("eero", "eero_beacon")

    @property
    def is_eero_beacon(self) -> bool:
        """Is Eero beacon."""
        return self._resource_type == "eero_beacon"

    @property
    def is_network(self) -> bool:
        """Is network."""
        return self._resource_type == "network"

    @property
    def is_profile(self) -> bool:
        """Is profile."""
        return self._resource_type == "profile"

    @property
    def url(self) -> str | None:
        """URL."""
        if self.is_account:
            return URL_ACCOUNT
        if self.is_backup_network:
            uuid = self.data.get("uuid")
            return f"{self.network.url}/backup_access_points/{uuid}"
        return self.data.get("url")
