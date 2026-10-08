"""Support for Eero select entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EeroConfigEntry, EeroEntity, EeroEntityDescription
from .const import (
    CONF_EEROS,
)


@dataclass
class EeroSelectEntityDescription(EeroEntityDescription, SelectEntityDescription):
    """Class to describe an Eero select entity."""

    entity_category: EntityCategory | None = EntityCategory.CONFIG


SELECT_DESCRIPTIONS: list[EeroSelectEntityDescription] = [
    EeroSelectEntityDescription(
        key="nightlight_mode",
        name="Nightlight Mode",
        options="nightlight_mode_options",
    ),
    EeroSelectEntityDescription(
        key="preferred_update_hour",
        name="Preferred Update Time",
        options="preferred_update_hour_options",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EeroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an Eero select entity based on a config entry."""
    data = config_entry.runtime_data
    coordinator = data.coordinator
    entities: list[EeroSelectEntity] = []

    SUPPORTED_KEYS = {
        description.key: description for description in SELECT_DESCRIPTIONS
    }

    for network in coordinator.data.networks:
        if network.id in data.networks:
            for key, description in SUPPORTED_KEYS.items():
                if description.premium_type and not network.premium_enabled:
                    continue
                if hasattr(network, key):
                    entities.append(
                        EeroSelectEntity(
                            coordinator,
                            network.id,
                            None,
                            description,
                            data.miscellaneous[network.id],
                        )
                    )

            for eero in network.eeros:
                if eero.id in data.resources[network.id][CONF_EEROS]:
                    for key, description in SUPPORTED_KEYS.items():
                        if description.premium_type and not network.premium_enabled:
                            continue
                        if hasattr(eero, key):
                            entities.append(
                                EeroSelectEntity(
                                    coordinator,
                                    network.id,
                                    eero.id,
                                    description,
                                    data.miscellaneous[network.id],
                                )
                            )

    async_add_entities(entities)


class EeroSelectEntity(SelectEntity, EeroEntity):
    """Representation of an Eero select entity."""

    entity_description: EeroSelectEntityDescription

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return getattr(self.resource, self.entity_description.options)

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return getattr(self.resource, self.entity_description.key)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await getattr(self.resource, f"async_set_{self.entity_description.key}")(option)
        if self.entity_description.request_refresh:
            await self.coordinator.async_request_refresh()
