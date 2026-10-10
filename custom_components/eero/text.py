"""Support for Eero text entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EeroConfigEntry, EeroEntity, EeroEntityDescription


@dataclass
class EeroTextEntityDescription(EeroEntityDescription, TextEntityDescription):
    """Class to describe an Eero text entity."""

    entity_category: EntityCategory | None = EntityCategory.CONFIG


TEXT_DESCRIPTIONS: list[EeroTextEntityDescription] = [
    EeroTextEntityDescription(
        key="dns_custom_ips",
        name="Custom DNS Servers",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EeroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an Eero text entity based on a config entry."""
    data = config_entry.runtime_data
    coordinator = data.coordinator
    entities: list[EeroTextEntity] = []

    SUPPORTED_KEYS = {description.key: description for description in TEXT_DESCRIPTIONS}

    for network in coordinator.data.networks:
        if network.id in data.networks:
            for key, description in SUPPORTED_KEYS.items():
                if description.premium_type and not network.premium_enabled:
                    continue
                if hasattr(network, key):
                    entities.append(
                        EeroTextEntity(
                            coordinator,
                            network.id,
                            None,
                            description,
                            data.miscellaneous[network.id],
                        )
                    )

    async_add_entities(entities)


class EeroTextEntity(EeroEntity, TextEntity):
    """Representation of an Eero text entity."""

    @property
    def native_value(self) -> str | None:
        """Return the current value."""
        return getattr(self.resource, self.entity_description.key) or ""

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        await getattr(self.resource, f"async_set_{self.entity_description.key}")(value)
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()
