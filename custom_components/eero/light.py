"""Support for Eero light entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EeroConfigEntry, EeroEntity, EeroEntityDescription
from .util import eero_allowed


@dataclass
class EeroLightEntityDescription(EeroEntityDescription, LightEntityDescription):
    """Class to describe an Eero light entity."""

    entity_category: EntityCategory | None = EntityCategory.CONFIG
    color_mode: ColorMode = ColorMode.BRIGHTNESS
    supported_color_modes: set[ColorMode] = field(default_factory=lambda: {ColorMode.BRIGHTNESS})
    brightness_key: str | None = None
    turn_on_action: str | None = None
    turn_off_action: str | None = None
    set_brightness_action: str | None = None


LIGHT_DESCRIPTIONS: list[EeroLightEntityDescription] = [
    EeroLightEntityDescription(
        key="nightlight_enabled",
        name="Nightlight",
        brightness_key="nightlight_brightness_percentage",
        turn_on_action="async_set_nightlight_ambient",
        turn_off_action="async_set_nightlight_disabled",
        set_brightness_action="async_set_nightlight_brightness_percentage",
    ),
    EeroLightEntityDescription(
        key="status_light_enabled",
        name="Status Light",
        brightness_key="status_light_brightness",
        turn_on_action="async_set_status_light_on",
        turn_off_action="async_set_status_light_off",
        set_brightness_action="async_set_status_light_brightness",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EeroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an Eero light entity based on a config entry."""
    data = config_entry.runtime_data
    coordinator = data.coordinator
    entities: list[EeroLightEntity] = []

    SUPPORTED_KEYS = {description.key: description for description in LIGHT_DESCRIPTIONS}

    for network in coordinator.data.networks:
        if network.id in data.networks:
            for eero in network.eeros:
                if eero_allowed(eero.id, data.resources[network.id]):
                    for key, description in SUPPORTED_KEYS.items():
                        if description.premium_type and not network.premium_enabled:
                            continue
                        if hasattr(eero, key):
                            entities.append(
                                EeroLightEntity(
                                    coordinator,
                                    network.id,
                                    eero.id,
                                    description,
                                    data.miscellaneous[network.id],
                                )
                            )

    async_add_entities(entities)


class EeroLightEntity(EeroEntity, LightEntity):
    """Representation of an Eero light entity."""

    entity_description: EeroLightEntityDescription

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return bool(getattr(self.resource, self.entity_description.key))

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        if self.entity_description.brightness_key:
            value = getattr(self.resource, self.entity_description.brightness_key)
            if value is not None:
                return int(value * 255 / 100)
        return None

    @property
    def color_mode(self) -> str:
        """Return the color mode of the light."""
        return self.entity_description.color_mode

    @property
    def supported_color_modes(self) -> set[str]:
        """Flag supported color modes."""
        return self.entity_description.supported_color_modes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if ATTR_BRIGHTNESS in kwargs and self.entity_description.set_brightness_action:
            brightness = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)
            await getattr(self.resource, self.entity_description.set_brightness_action)(value=brightness)
        elif self.entity_description.turn_on_action:
            await getattr(self.resource, self.entity_description.turn_on_action)()
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if self.entity_description.turn_off_action:
            await getattr(self.resource, self.entity_description.turn_off_action)()
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()
