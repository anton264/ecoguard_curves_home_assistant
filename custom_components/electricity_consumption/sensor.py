"""Sensor platform for Electricity Consumption integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CURRENT_POWER,
    ATTR_DAILY_CONSUMPTION,
    ATTR_LAST_UPDATE,
    ATTR_LATEST_READING,
    ATTR_MONTHLY_CONSUMPTION,
    ATTR_YEARLY_CONSUMPTION,
    DOMAIN,
)
from .coordinator import CurvesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Electricity Consumption sensor from a config entry."""
    coordinator: CurvesDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entity = ElectricityConsumptionSensor(coordinator, config_entry)
    async_add_entities([entity])


class ElectricityConsumptionSensor(
    CoordinatorEntity[CurvesDataUpdateCoordinator], SensorEntity
):
    """Representation of an Electricity Consumption sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: CurvesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the Electricity Consumption sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"Electricity Consumption (Curves)"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            consumption = self.coordinator.data.get("consumption", 0.0)
            return round(consumption, 3) if consumption is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        data = self.coordinator.data
        attrs: dict[str, Any] = {
            ATTR_CURRENT_POWER: round(data.get("current_power", 0.0), 2),
            ATTR_DAILY_CONSUMPTION: round(data.get("daily_consumption", 0.0), 3),
            ATTR_MONTHLY_CONSUMPTION: round(
                data.get("monthly_consumption", 0.0), 3
            ),
            ATTR_YEARLY_CONSUMPTION: round(data.get("yearly_consumption", 0.0), 3),
            ATTR_LATEST_READING: data.get("latest_reading"),
        }
        
        # Add last update time if available
        if hasattr(self.coordinator, "last_update_success_time") and self.coordinator.last_update_success_time:
            attrs[ATTR_LAST_UPDATE] = self.coordinator.last_update_success_time.isoformat()
        
        return attrs
