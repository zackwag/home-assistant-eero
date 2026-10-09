"""Eero API."""

from __future__ import annotations

from .const import METHOD_PUT
from .resource import EeroResource
from .util import generate_qr_code


class EeroGuestNetwork(EeroResource):
    """EeroGuestNetwork."""

    _resource_type = "guest_network"

    @property
    def enabled(self) -> bool | None:
        """Enabled."""
        return self.data.get("enabled")

    async def async_set_enabled(self, value: bool) -> None:
        """Set enabled."""
        if not isinstance(value, bool):
            return
        await self.api.call(
            method=METHOD_PUT,
            url=f"/2.2/networks/{self.network.id}/guestnetwork",
            json={
                "enabled": value,
            },
        )

    @property
    def connected_clients_count(self) -> int:
        """Connected clients count."""
        return self.network.connected_guest_clients_count

    @property
    def id(self) -> str | None:
        """ID."""
        return f"{self.network.id}-guest"

    @property
    def name(self) -> str | None:
        """Name."""
        return self.ssid or "Guest Network"

    @property
    def password(self) -> str | None:
        """Password."""
        return self.data.get("password")

    @property
    def qr_code(self) -> bytes | None:
        """QR code."""
        if not self.enabled and self.api.show_eero_logo.get(self.network.id):
            return self.api.default_qr_code
        return generate_qr_code(
            ssid=self.ssid,
            password=self.password,
        )

    @property
    def ssid(self) -> str | None:
        """SSID."""
        return self.data.get("name")
