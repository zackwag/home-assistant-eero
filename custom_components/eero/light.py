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
    supported_color_modes: set[ColorMode] = field(
        default_factory=lambda: {ColorMode.BRIGHTNESS}
    )


LIGHT_DESCRIPTIONS: list[EeroLightEntityDescription] = [
    EeroLightEntityDescription(
        key="status_light_enabled",
        name="Status Light",
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

    SUPPORTED_KEYS = {
        description.key: description for description in LIGHT_DESCRIPTIONS
    }

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

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return bool(getattr(self.resource, self.entity_description.key))

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return int(self.resource.status_light_brightness * 255 / 100)

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
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)
            await self.resource.async_set_status_light_brightness(value=brightness)
        else:
            await self.resource.async_set_status_light_on()
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.resource.async_set_status_light_off()
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()
