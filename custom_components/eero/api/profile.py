"""Eero API."""

from __future__ import annotations

from datetime import datetime

from .client import EeroClient
from .resource import EeroResource


class EeroProfile(EeroResource):
    """EeroProfile."""

    _resource_type = "profile"

    @property
    def adblock_day(self) -> int | None:
        """Adblock day."""
        for entry in self.network.data.get("activity", {}).get("profiles", {}).get("adblock_day", {}).get(self.id, []):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def adblock_month(self) -> int | None:
        """Adblock month."""
        for entry in (
            self.network.data.get("activity", {}).get("profiles", {}).get("adblock_month", {}).get(self.id, [])
        ):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def adblock_week(self) -> int | None:
        """Adblock week."""
        for entry in self.network.data.get("activity", {}).get("profiles", {}).get("adblock_week", {}).get(self.id, []):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def block_apps_enabled(self) -> bool:
        """Block apps enabled."""
        return bool(self.blocked_applications)

    @property
    def blocked_applications(self) -> list[str]:
        """Blocked applications."""
        return self.data.get("premium_dns", {}).get("blocked_applications", [])

    @property
    def blocked_applications_count(self) -> int:
        """Blocked applications count."""
        return len(self.blocked_applications)

    async def async_set_blocked_applications(self, blocked_applications: list) -> None:
        """Set blocked application."""
        if not isinstance(blocked_applications, list):
            return
        await self.api.lib.dns_policies.set_profile_blocked_applications(self.network.id, self.id, blocked_applications)

    @property
    def blocked_day(self) -> int | None:
        """Blocked day."""
        for entry in self.network.data.get("activity", {}).get("profiles", {}).get("blocked_day", {}).get(self.id, []):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def blocked_month(self) -> int | None:
        """Blocked month."""
        for entry in (
            self.network.data.get("activity", {}).get("profiles", {}).get("blocked_month", {}).get(self.id, [])
        ):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def blocked_week(self) -> int | None:
        """Blocked week."""
        for entry in self.network.data.get("activity", {}).get("profiles", {}).get("blocked_week", {}).get(self.id, []):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def connected(self) -> bool:
        """Connected."""
        return bool(self.connected_clients_count != 0)

    @property
    def connected_clients_count(self) -> int:
        """Connected clients count."""
        return len(self.connected_clients_names)

    @property
    def connected_clients_names(self) -> list[str]:
        """Connected clients names."""
        return [client.name for client in self.clients if client.connected]

    @property
    def data_usage_day(self) -> tuple[int | None, int | None]:
        """Data usage day."""
        down, up = None, None
        for series in (
            self.network.data.get("activity", {}).get("profiles", {}).get("data_usage_day", {}).get(self.id, [])
        ):
            if series["type"] == "download":
                down = series["sum"]
            elif series["type"] == "upload":
                up = series["sum"]
        return (down, up)

    @property
    def data_usage_month(self) -> tuple[int | None, int | None]:
        """Data usage month."""
        down, up = None, None
        for series in (
            self.network.data.get("activity", {}).get("profiles", {}).get("data_usage_month", {}).get(self.id, [])
        ):
            if series["type"] == "download":
                down = series["sum"]
            elif series["type"] == "upload":
                up = series["sum"]
        return (down, up)

    @property
    def data_usage_week(self) -> tuple[int | None, int | None]:
        """Data usage week."""
        down, up = None, None
        for series in (
            self.network.data.get("activity", {}).get("profiles", {}).get("data_usage_week", {}).get(self.id, [])
        ):
            if series["type"] == "download":
                down = series["sum"]
            elif series["type"] == "upload":
                up = series["sum"]
        return (down, up)

    @property
    def inspected_day(self) -> int | None:
        """Inspected day."""
        for entry in (
            self.network.data.get("activity", {}).get("profiles", {}).get("inspected_day", {}).get(self.id, [])
        ):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def inspected_month(self) -> int | None:
        """Inspected month."""
        for entry in (
            self.network.data.get("activity", {}).get("profiles", {}).get("inspected_month", {}).get(self.id, [])
        ):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def inspected_week(self) -> int | None:
        """Inspected week."""
        for entry in (
            self.network.data.get("activity", {}).get("profiles", {}).get("inspected_week", {}).get(self.id, [])
        ):
            if entry["insights_url"] == self.url_insights:
                return entry["sum"]
        return None

    @property
    def last_active(self) -> datetime | None:
        """Last active."""
        if last_active := [client.last_active for client in self.clients if client.last_active is not None]:
            return max(last_active)
        return None

    @property
    def name(self) -> str | None:
        """Name."""
        return self.data.get("name")

    @property
    def name_long(self) -> str:
        """Name long."""
        return f"{self.name} Profile"

    @property
    def paused(self) -> bool | None:
        """Paused."""
        return self.data.get("paused")

    async def async_set_paused(self, value: bool) -> None:
        """Set paused."""
        if not isinstance(value, bool):
            return
        await self.api.lib.profiles.pause_profile(self.network.id, self.id, value)

    @property
    def url_insights(self) -> str | None:
        """URL insights."""
        return f"{self.network.url_insights}/profiles/{self.id}"

    @property
    def clients(self) -> list[EeroClient | None]:
        """Clients."""
        return [EeroClient(self.api, self, client) for client in self.data.get("devices", [])]
