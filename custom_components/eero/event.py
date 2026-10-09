"""Support for Eero event entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.event import EventEntity, EventEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EeroConfigEntry, EeroEntity, EeroEntityDescription


@dataclass
class EeroEventEntityDescription(EeroEntityDescription, EventEntityDescription):
    """Class to describe an Eero event entity."""

    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC


EVENT_DESCRIPTIONS: list[EeroEventEntityDescription] = [
    EeroEventEntityDescription(
        key="latest_notification",
        name="Network Event",
        event_types=["new_client", "speed_test", "firmware_update", "outage", "backup_internet", "notification"],
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EeroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an Eero event entity based on a config entry."""
    data = config_entry.runtime_data
    coordinator = data.coordinator
    entities: list[EeroEventEntity] = []

    for network in coordinator.data.networks:
        if network.id in data.networks:
            for description in EVENT_DESCRIPTIONS:
                entities.append(
                    EeroEventEntity(
                        coordinator,
                        network.id,
                        None,
                        description,
                        data.miscellaneous[network.id],
                    )
                )

    async_add_entities(entities)


class EeroEventEntity(EeroEntity, EventEntity):
    """Representation of an Eero event entity."""

    def __init__(self, coordinator, network_id, resource_id, description, miscellaneous) -> None:
        """Initialize."""
        super().__init__(coordinator, network_id, resource_id, description, miscellaneous)
        self._last_notification_id: str | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.resource is None:
            super()._handle_coordinator_update()
            return

        notification = self.resource.latest_notification
        if notification is None:
            super()._handle_coordinator_update()
            return

        notification_id = notification.get("id") or notification.get("timestamp")
        if notification_id and notification_id != self._last_notification_id:
            self._last_notification_id = notification_id
            event_type = self._classify_event(notification)
            self._trigger_event(
                event_type,
                {
                    "title": notification.get("title", ""),
                    "body": notification.get("body", ""),
                    "timestamp": notification.get("timestamp", ""),
                },
            )

        super()._handle_coordinator_update()

    @staticmethod
    def _classify_event(notification: dict) -> str:
        """Classify a notification into an event type."""
        title = (notification.get("title") or "").lower()
        body = (notification.get("body") or "").lower()
        text = f"{title} {body}"
        if "new device" in text or "joined" in text:
            return "new_client"
        if "speed test" in text or "speedtest" in text:
            return "speed_test"
        if "update" in text or "firmware" in text:
            return "firmware_update"
        if "offline" in text or "outage" in text or "down" in text:
            return "outage"
        if "backup" in text:
            return "backup_internet"
        return "notification"
