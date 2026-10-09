"""Support for Eero device tracker entities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.const import ATTR_MANUFACTURER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import EeroConfigEntry, EeroEntity, EeroEntityDescription
from .const import CONF_CONSIDER_HOME
from .util import client_allowed, profile_allowed


@dataclass
class EeroDeviceTrackerEntityDescription(EeroEntityDescription):
    """Class to describe an Eero device tracker entity."""

    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC


DEVICE_TRACKER_DESCRIPTIONS: list[EeroDeviceTrackerEntityDescription] = [
    EeroDeviceTrackerEntityDescription(
        key="device_tracker",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EeroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an Eero device tracker entity based on a config entry."""
    data = config_entry.runtime_data
    coordinator = data.coordinator
    entities: list[EeroDeviceTrackerEntity] = []

    SUPPORTED_KEYS = {description.key: description for description in DEVICE_TRACKER_DESCRIPTIONS}

    for network in coordinator.data.networks:
        if network.id in data.networks:
            for profile in network.profiles:
                if profile_allowed(profile.id, data.resources[network.id]):
                    for description in SUPPORTED_KEYS.values():
                        if description.premium_type and not network.premium_enabled:
                            continue
                        entities.append(
                            EeroDeviceTrackerEntity(
                                coordinator,
                                network.id,
                                profile.id,
                                description,
                                data.miscellaneous[network.id],
                            )
                        )

            for client in network.clients:
                if client_allowed(client, data.resources[network.id]):
                    for description in SUPPORTED_KEYS.values():
                        if description.premium_type and not network.premium_enabled:
                            continue
                        entities.append(
                            EeroDeviceTrackerEntity(
                                coordinator,
                                network.id,
                                client.id,
                                description,
                                data.miscellaneous[network.id],
                            )
                        )

    async_add_entities(entities)


class EeroDeviceTrackerEntity(ScannerEntity, EeroEntity):
    """Representation of an Eero device tracker entity."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = None
    _attr_source_type = SourceType.ROUTER

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        network_id: str,
        resource_id: str,
        description: EeroDeviceTrackerEntityDescription,
        miscellaneous: dict[str, Any],
    ) -> None:
        """Initialize device."""
        super().__init__(
            coordinator,
            network_id,
            resource_id,
            description,
            miscellaneous,
        )
        self.consider_home: timedelta = timedelta(minutes=miscellaneous[CONF_CONSIDER_HOME])
        self.last_seen: datetime | None = None

    @property
    def is_connected(self) -> bool | None:
        """Return true if the device is connected to the network."""
        if self.consider_home:
            if not self.resource.connected:
                return bool(self.last_seen and (dt_util.utcnow() - self.last_seen) < self.consider_home)
            self.last_seen = dt_util.utcnow()
            return True
        return self.resource.connected

    @property
    def ip_address(self) -> str | None:
        """Return the primary ip address of the device."""
        if self.resource.is_client:
            return self.resource.ip
        return None

    @property
    def mac_address(self) -> str | None:
        """Return the mac address of the device."""
        if self.resource.is_client:
            return self.resource.mac
        return None

    @property
    def hostname(self) -> str | None:
        """Return hostname of the device."""
        if self.resource.is_client:
            return self.resource.hostname
        return None

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        attrs = {}
        if self.resource.is_client:
            if location := self.resource.source_location:
                attrs["connected_to"] = location
                attrs["connected_to_model"] = self.resource.source_model
            if self.is_connected:
                attrs["connection_type"] = self.resource.connection_type
                attrs["ip_address"] = self.resource.ip
                if manufacturer := self.resource.manufacturer:
                    attrs[ATTR_MANUFACTURER] = manufacturer
                attrs["network_name"] = self.network.name
                if self.resource.wireless:
                    frequency, frequency_unit = self.resource.interface_frequency
                    if frequency:
                        attrs["band"] = f"{frequency} {frequency_unit}".strip() if frequency_unit else str(frequency)
                    if self.resource.channel is not None:
                        attrs["channel"] = self.resource.channel
                    if channel_width := self.resource.channel_width_rx:
                        attrs["channel_width"] = channel_width
        return attrs
