"""Eero API."""

from __future__ import annotations

from datetime import time

from .const import (
    METHOD_PUT,
    STATE_AMBIENT,
    STATE_DISABLED,
    STATE_SCHEDULE,
)
from .firmware import EeroFirmware
from .resource import EeroResource


class EeroDevice(EeroResource):
    """EeroDevice."""

    _resource_type = "eero"

    @property
    def connected_clients_count(self) -> int | None:
        """Connected clients counts."""
        return self.data.get("connected_clients_count")

    @property
    def connected_clients_names(self) -> list[str]:
        """Connected clients names."""
        return [client.name for client in self.network.clients if client.source_location == self.name]

    @property
    def current_firmware(self) -> EeroFirmware:
        """Current firmware."""
        history = {firmware.os_version: firmware for firmware in self.network.firmware_history}
        return history.get(self.os_version.split("-")[0], EeroFirmware())

    @property
    def data_usage_day(self) -> tuple[int | None, int | None]:
        """Data usage day."""
        for eero in self.network.data.get("activity", {}).get("eeros", {}).get("data_usage_day", []):
            if eero["url"] == self.url:
                return (eero["download"], eero["upload"])
        return (None, None)

    @property
    def data_usage_month(self) -> tuple[int | None, int | None]:
        """Data usage month."""
        for eero in self.network.data.get("activity", {}).get("eeros", {}).get("data_usage_month", []):
            if eero["url"] == self.url:
                return (eero["download"], eero["upload"])
        return (None, None)

    @property
    def data_usage_week(self) -> tuple[int | None, int | None]:
        """Data usage week."""
        for eero in self.network.data.get("activity", {}).get("eeros", {}).get("data_usage_week", []):
            if eero["url"] == self.url:
                return (eero["download"], eero["upload"])
        return (None, None)

    @property
    def is_gateway(self) -> bool | None:
        """Is gateway."""
        return self.data.get("gateway")

    @property
    def location(self) -> str | None:
        """Location."""
        return self.data.get("location")

    @property
    def mac_address(self) -> str | None:
        """MAC address."""
        return self.data.get("mac_address")

    @property
    def model(self) -> str | None:
        """Model."""
        return self.data.get("model")

    @property
    def model_number(self) -> str | None:
        """Model number."""
        return self.data.get("model_number")

    @property
    def name(self) -> str | None:
        """Name."""
        return self.location

    @property
    def name_long(self) -> str:
        """Name long."""
        return f"{self.name} Eero"

    @property
    def os_version(self) -> str | None:
        """OS version."""
        return self.data.get("os_version")

    async def async_led_cycle(self) -> None:
        """Flash LED to identify this eero."""
        await self.api.lib.eeros.led_cycle(self.serial)

    async def async_reboot(self) -> None:
        """Reboot."""
        await self.api.lib.eeros.reboot_eero(self.id, network_id=self.network.id)

    @property
    def serial(self) -> str | None:
        """Serial."""
        return self.data.get("serial")

    async def async_set_status_light(self, value: bool) -> None:
        """Set status light."""
        if not isinstance(value, bool):
            return
        await self.api.lib.eeros.set_led(self.id, network_id=self.network.id, enabled=value)

    async def async_set_status_light_brightness(self, value: int) -> None:
        """Set status light brightness."""
        if not isinstance(value, int):
            return
        if not value:
            await self.async_set_status_light_off()
            return
        await self.api.lib.eeros.set_led_brightness(self.id, network_id=self.network.id, brightness=value)

    async def async_set_status_light_off(self) -> None:
        """Set status light off."""
        await self.async_set_status_light(value=False)

    async def async_set_status_light_on(self) -> None:
        """Set status light on."""
        await self.async_set_status_light(value=True)

    @property
    def status(self) -> str | None:
        """Status."""
        return self.data.get("status")

    @property
    def status_light_brightness(self) -> int | None:
        """Status light brightness."""
        return self.data.get("led_brightness")

    @property
    def status_light_enabled(self) -> bool | None:
        """Status light enabled."""
        return self.data.get("led_on")

    @property
    def support_expiration_string(self) -> str | None:
        """Support expiration string."""
        return self.data.get("update_status", {}).get("support_expiration_string")

    @property
    def support_expired(self) -> bool | None:
        """Support expired."""
        return self.data.get("update_status", {}).get("support_expired")

    @property
    def target_firmware(self) -> EeroFirmware:
        """Target firmware."""
        if self.support_expired:
            return self.current_firmware
        return self.network.target_firmware

    @property
    def update_available(self) -> bool | None:
        """Update available."""
        return self.data.get("update_available")

    @property
    def url_led(self) -> str | None:
        """URL led."""
        return self.data.get("resources", {}).get("led_action")

    @property
    def url_reboot(self) -> str | None:
        """URL reboot."""
        return self.data.get("resources", {}).get("reboot")


class EeroDeviceBeacon(EeroDevice):
    """EeroDeviceBeacon."""

    _resource_type = "eero_beacon"

    def _format_time(self, value: int) -> str | None:
        if not isinstance(value, int):
            return None
        if value < 10:
            return f"0{value}"
        return str(value)

    @property
    def nightlight_brightness_percentage(self) -> int | None:
        """Nightlight brightness percentage."""
        return self.data.get("nightlight", {}).get("brightness_percentage")

    async def async_set_nightlight_brightness_percentage(self, value: float) -> None:
        """Set nightlight brightness percentage."""
        if not isinstance(value, (float, int)):
            return
        await self.async_set_nightlight_brightness(value=int(value))

    @property
    def nightlight_enabled(self) -> bool | None:
        """Nightlight enabled."""
        return self.data.get("nightlight", {}).get("enabled")

    @property
    def nightlight_mode(self) -> str:
        """Nightlight mode."""
        if not self.nightlight_enabled:
            return STATE_DISABLED
        if not self.nightlight_schedule_enabled:
            return STATE_AMBIENT
        return STATE_SCHEDULE

    async def async_set_nightlight_mode(self, value: str) -> None:
        """Set nightlight mode."""
        if value == STATE_DISABLED:
            await self.async_set_nightlight_disabled()
        if value == STATE_AMBIENT:
            await self.async_set_nightlight_ambient()
        if value == STATE_SCHEDULE:
            await self.async_set_nightlight_schedule()

    @property
    def nightlight_mode_options(self) -> list[str]:
        """Nightlight mode options."""
        return [STATE_AMBIENT, STATE_DISABLED, STATE_SCHEDULE]

    @property
    def nightlight_schedule(self) -> tuple[str | None, str | None]:
        """Nightlight schedule."""
        return (
            self.data.get("nightlight", {}).get("schedule", {}).get("on"),
            self.data.get("nightlight", {}).get("schedule", {}).get("off"),
        )

    @property
    def nightlight_schedule_enabled(self) -> bool | None:
        """Nightlight schedule enabled."""
        return self.data.get("nightlight", {}).get("schedule", {}).get("enabled")

    @property
    def nightlight_schedule_off(self) -> time:
        """Nightlight schedule off."""
        return time(
            hour=int(self.nightlight_schedule_off_hour),
            minute=int(self.nightlight_schedule_off_minute),
        )

    async def async_set_nightlight_schedule_off(self, value: time) -> None:
        """Set nightlight schedule off."""
        if not isinstance(value, time):
            return
        await self.async_set_nightlight_schedule(
            time_on=self.nightlight_schedule[0],
            time_off=f"{self._format_time(value.hour)}:{self._format_time(value.minute)}",
        )

    @property
    def nightlight_schedule_off_hour(self) -> str:
        """Nightlight schedule off hour."""
        return self.nightlight_schedule[1].split(":")[0]

    @property
    def nightlight_schedule_off_minute(self) -> str:
        """Nightlight schedule off minute."""
        return self.nightlight_schedule[1].split(":")[1]

    @property
    def nightlight_schedule_on(self) -> time:
        """Nightlight schedule on."""
        return time(
            hour=int(self.nightlight_schedule_on_hour),
            minute=int(self.nightlight_schedule_on_minute),
        )

    async def async_set_nightlight_schedule_on(self, value: time) -> None:
        """Set nightlight schedule on."""
        if not isinstance(value, time):
            return
        await self.async_set_nightlight_schedule(
            time_on=f"{self._format_time(value.hour)}:{self._format_time(value.minute)}",
            time_off=self.nightlight_schedule[1],
        )

    @property
    def nightlight_schedule_on_hour(self) -> str:
        """Nightlight schedule on hour."""
        return self.nightlight_schedule[0].split(":")[0]

    @property
    def nightlight_schedule_on_minute(self) -> str:
        """Nightlight schedule on minute."""
        return self.nightlight_schedule[0].split(":")[1]

    async def _async_set_nightlight(self, json: dict) -> None:
        if not isinstance(json, dict):
            return
        await self.api.call(
            method=METHOD_PUT,
            url=f"/2.2/eeros/{self.id}/nightlight/settings",
            json=json,
        )

    async def async_set_nightlight_ambient(self) -> None:
        """Set nightlight ambient."""
        await self._async_set_nightlight(
            json={
                "enabled": True,
                "schedule": {
                    "enabled": False,
                },
            },
        )

    async def async_set_nightlight_brightness(self, value: int) -> None:
        """Set nightlight brightness."""
        if not isinstance(value, int):
            return
        await self._async_set_nightlight(
            json={
                "enabled": True,
                "brightness_percentage": value,
                "schedule": {
                    "enabled": True,
                    "on": self.nightlight_schedule[0],
                    "off": self.nightlight_schedule[1],
                },
            },
        )

    async def async_set_nightlight_disabled(self) -> None:
        """Set nightlight disabled."""
        await self._async_set_nightlight(
            json={
                "enabled": False,
            },
        )

    async def async_set_nightlight_schedule(self, time_on: str | None = None, time_off: str | None = None) -> None:
        """Set nightlight schedule."""
        if time_on is None:
            time_on = self.nightlight_schedule[0]
        if time_off is None:
            time_off = self.nightlight_schedule[1]
        if not isinstance(time_on, str) or not isinstance(time_off, str):
            return
        await self._async_set_nightlight(
            json={
                "enabled": True,
                "schedule": {
                    "enabled": True,
                    "on": time_on,
                    "off": time_off,
                },
            },
        )
