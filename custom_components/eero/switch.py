"""Support for Eero switch entities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EeroConfigEntry, EeroEntity, EeroEntityDescription
from .util import backup_network_allowed, client_allowed, profile_allowed


@dataclass
class EeroSwitchEntityDescription(EeroEntityDescription, SwitchEntityDescription):
    """Class to describe an Eero switch entity."""

    device_class: SwitchDeviceClass | None = SwitchDeviceClass.SWITCH
    entity_category: EntityCategory | None = EntityCategory.CONFIG


SWITCH_DESCRIPTIONS: list[EeroSwitchEntityDescription] = [
    EeroSwitchEntityDescription(
        key="auto_join_enabled",
        name="Auto-Join Enabled",
        premium_type=True,
    ),
    EeroSwitchEntityDescription(
        key="backup_internet_enabled",
        name="Backup Internet Enabled",
        premium_type=True,
    ),
    EeroSwitchEntityDescription(
        key="band_steering",
        name="Band Steering",
    ),
    EeroSwitchEntityDescription(
        key="ddns_enabled",
        name="Dynamic DNS",
        premium_type=True,
        extra_attrs={
            "domain": lambda resource: resource.ddns_subdomain,
        },
    ),
    EeroSwitchEntityDescription(
        key="dns_caching",
        name="Local DNS Caching",
        request_refresh=False,
    ),
    EeroSwitchEntityDescription(
        key="fast_transition",
        name="Fast Transition (802.11r)",
        request_refresh=False,
    ),
    EeroSwitchEntityDescription(
        key="ipv6_upstream",
        name="IPv6 Enabled",
        request_refresh=False,
    ),
    EeroSwitchEntityDescription(
        key="mlo_mode",
        name="Multi-Link Operation (Wi-Fi 7)",
        request_refresh=False,
    ),
    EeroSwitchEntityDescription(
        key="pause_5g_enabled",
        name="5 GHz Band Paused",
        extra_attrs={
            "expiration": lambda resource: resource.pause_5g_expiration,
        },
    ),
    EeroSwitchEntityDescription(
        key="passpoint_enabled",
        name="Passpoint (Hotspot 2.0)",
        request_refresh=False,
    ),
    EeroSwitchEntityDescription(
        key="paused",
        name="Paused",
    ),
    EeroSwitchEntityDescription(
        key="power_saving_enabled",
        name="Power Saving",
        extra_attrs={
            "schedules": lambda resource: resource.power_saving_schedules,
        },
    ),
    EeroSwitchEntityDescription(
        key="secondary_wan_deny_access",
        name="Allow Internet Backup",
        premium_type=True,
    ),
    EeroSwitchEntityDescription(
        key="sqm",
        name="Smart Queue Management",
    ),
    EeroSwitchEntityDescription(
        key="thread_enabled",
        name="Thread Enabled",
        extra_attrs={
            "thread_network_key": lambda resource: resource.thread_master_key,
            "thread_network_name": lambda resource: resource.thread_name,
            "channel": lambda resource: resource.thread_channel,
            "pan_id": lambda resource: resource.thread_pan_id,
            "extended_pan_id": lambda resource: resource.thread_xpan_id,
            "commissioning_credential": lambda resource: resource.thread_commissioning_credential,
            "active_operational_dataset": lambda resource: resource.thread_active_operational_dataset,
        },
    ),
    EeroSwitchEntityDescription(
        key="upnp",
        name="UPnP",
    ),
    EeroSwitchEntityDescription(
        key="wpa3",
        name="WPA3",
    ),
]

GUEST_NETWORK_SWITCH_DESCRIPTIONS: list[EeroSwitchEntityDescription] = [
    EeroSwitchEntityDescription(
        key="enabled",
        name="Enabled",
        extra_attrs={
            "ssid": lambda resource: resource.ssid,
            "password": lambda resource: resource.password,
            "connected_clients": lambda resource: resource.connected_clients_count,
        },
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EeroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an Eero switch entity based on a config entry."""
    data = config_entry.runtime_data
    coordinator = data.coordinator
    entities: list[EeroSwitchEntity] = []

    SUPPORTED_KEYS = {description.key: description for description in SWITCH_DESCRIPTIONS}

    for network in coordinator.data.networks:
        if network.id in data.networks:
            for key, description in SUPPORTED_KEYS.items():
                if description.premium_type and not network.premium_enabled:
                    continue
                if hasattr(network, key):
                    entities.append(
                        EeroSwitchEntity(
                            coordinator,
                            network.id,
                            None,
                            description,
                            data.miscellaneous[network.id],
                        )
                    )

            for backup_network in network.backup_networks:
                if backup_network_allowed(backup_network.id, data.resources[network.id]):
                    for key, description in SUPPORTED_KEYS.items():
                        if hasattr(backup_network, key):
                            entities.append(
                                EeroSwitchEntity(
                                    coordinator,
                                    network.id,
                                    backup_network.id,
                                    description,
                                    data.miscellaneous[network.id],
                                )
                            )

            guest_network = network.guest_network
            if guest_network:
                for description in GUEST_NETWORK_SWITCH_DESCRIPTIONS:
                    if hasattr(guest_network, description.key):
                        entities.append(
                            EeroSwitchEntity(
                                coordinator,
                                network.id,
                                guest_network.id,
                                description,
                                data.miscellaneous[network.id],
                            )
                        )

            for profile in network.profiles:
                if profile_allowed(profile.id, data.resources[network.id]):
                    for key, description in SUPPORTED_KEYS.items():
                        if description.premium_type and not network.premium_enabled:
                            continue
                        if hasattr(profile, key):
                            entities.append(
                                EeroSwitchEntity(
                                    coordinator,
                                    network.id,
                                    profile.id,
                                    description,
                                    data.miscellaneous[network.id],
                                )
                            )

            for client in network.clients:
                if client_allowed(client, data.resources[network.id]):
                    for key, description in SUPPORTED_KEYS.items():
                        if description.premium_type and not network.premium_enabled:
                            continue
                        if hasattr(client, key):
                            entities.append(
                                EeroSwitchEntity(
                                    coordinator,
                                    network.id,
                                    client.id,
                                    description,
                                    data.miscellaneous[network.id],
                                )
                            )

            for forward in network.port_forwards:
                fwd_desc = forward.get("description", "")
                fwd_port = forward.get("gateway_port", "")
                fwd_id = forward.get("url") or f"{fwd_desc}-{fwd_port}"
                entities.append(
                    EeroPortForwardEntity(
                        coordinator,
                        network.id,
                        fwd_id,
                        forward,
                        data.miscellaneous[network.id],
                    )
                )

    async_add_entities(entities)


class EeroSwitchEntity(EeroEntity, SwitchEntity):
    """Representation of an Eero switch entity."""

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return bool(getattr(self.resource, self.entity_description.key))

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes.

        Implemented by platform classes. Convention for attribute names
        is lowercase snake_case.
        """
        attrs = {}
        if self.entity_description.extra_attrs and self.is_on:
            for key, func in self.entity_description.extra_attrs.items():
                attrs[key] = func(self.resource)
        return attrs

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await getattr(self.resource, f"async_set_{self.entity_description.key}")(True)
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await getattr(self.resource, f"async_set_{self.entity_description.key}")(False)
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()


class EeroPortForwardEntity(CoordinatorEntity, SwitchEntity):
    """Representation of an eero port forward switch."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(self, coordinator, network_id, forward_id, forward_data, miscellaneous) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._network_id = network_id
        self._forward_id = forward_id
        self._forward_data = forward_data
        desc = forward_data.get("description", "")
        port = forward_data.get("gateway_port", "")
        self._attr_name = f"Port Forward {desc or port}" if desc or port else "Port Forward"
        self._attr_unique_id = f"{network_id}-port-forward-{forward_id}"
        self._attr_icon = "mdi:lan-connect"

    @property
    def _network(self):
        for network in self.coordinator.data.networks:
            if network.id == self._network_id:
                return network
        return None

    @property
    def _current_forward(self) -> dict | None:
        """Find the current forward data from the latest update."""
        network = self._network
        if not network:
            return None
        for forward in network.port_forwards:
            if forward.get("url") == self._forward_id or forward.get("url") == self._forward_data.get("url"):
                self._forward_data = forward
                return forward
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._current_forward is not None

    @property
    def device_info(self):
        """Return device info linking to the network device."""
        from .const import DOMAIN

        return {"identifiers": {(DOMAIN, self._network_id)}}

    @property
    def is_on(self) -> bool | None:
        """Return True if the port forward is enabled."""
        forward = self._current_forward
        if forward:
            return forward.get("enabled", False)
        return None

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return port forward details."""
        forward = self._current_forward or self._forward_data
        return {
            "ip": forward.get("ip"),
            "protocol": forward.get("protocol"),
            "gateway_port": forward.get("gateway_port"),
            "client_port": forward.get("client_port"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the port forward."""
        forward = self._current_forward or self._forward_data
        url = forward.get("url")
        if url and self._network:
            await self._network.async_set_port_forward_enabled(url, forward, True)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the port forward."""
        forward = self._current_forward or self._forward_data
        url = forward.get("url")
        if url and self._network:
            await self._network.async_set_port_forward_enabled(url, forward, False)
            await self.coordinator.async_request_refresh()
