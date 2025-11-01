"""Sensor platform for EcoGuard Curves integration."""
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
    """Set up EcoGuard Curves sensors from a config entry."""
    coordinator: CurvesDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        ElectricityConsumptionSensor(coordinator, config_entry),
        ElectricityDailyConsumptionSensor(coordinator, config_entry),
        ElectricityMonthlyConsumptionSensor(coordinator, config_entry),
        ElectricityPriceSensor(coordinator, config_entry),
        ElectricityDailyPriceSensor(coordinator, config_entry),
        ElectricityMonthlyPriceSensor(coordinator, config_entry),
    ]
    
    async_add_entities(entities)


class ElectricityConsumptionSensor(
    CoordinatorEntity[CurvesDataUpdateCoordinator], SensorEntity
):
    """Representation of total Electricity Consumption sensor."""

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
        self._attr_name = f"Electricity Consumption"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_consumption"

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
            ATTR_LATEST_READING: data.get("latest_reading"),
        }
        
        # Add last update time if available
        if hasattr(self.coordinator, "last_update_success_time") and self.coordinator.last_update_success_time:
            attrs[ATTR_LAST_UPDATE] = self.coordinator.last_update_success_time.isoformat()
        
        return attrs


class ElectricityDailyConsumptionSensor(
    CoordinatorEntity[CurvesDataUpdateCoordinator], SensorEntity
):
    """Representation of daily Electricity Consumption sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: CurvesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the daily Electricity Consumption sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"Electricity Daily Consumption"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_daily_consumption"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            consumption = self.coordinator.data.get("daily_consumption", 0.0)
            return round(consumption, 3) if consumption is not None else None
        return None


class ElectricityMonthlyConsumptionSensor(
    CoordinatorEntity[CurvesDataUpdateCoordinator], SensorEntity
):
    """Representation of monthly Electricity Consumption sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: CurvesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the monthly Electricity Consumption sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"Electricity Monthly Consumption"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_monthly_consumption"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            consumption = self.coordinator.data.get("monthly_consumption", 0.0)
            return round(consumption, 3) if consumption is not None else None
        return None


class ElectricityPriceSensor(
    CoordinatorEntity[CurvesDataUpdateCoordinator], SensorEntity
):
    """Representation of current Electricity Cost sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: CurvesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the Electricity Cost sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        currency = config_entry.data.get("currency") or config_entry.options.get("currency", "EUR")
        self._attr_native_unit_of_measurement = currency
        self._attr_name = f"Electricity Cost"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_cost"

    @property
    def native_value(self) -> float | None:
        """Return the cost for the latest period."""
        if self.coordinator.data:
            cost = self.coordinator.data.get("current_cost", 0.0)
            return round(cost, 4) if cost is not None else None
        return None


class ElectricityDailyPriceSensor(
    CoordinatorEntity[CurvesDataUpdateCoordinator], SensorEntity
):
    """Representation of daily Electricity Cost sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: CurvesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the daily Electricity Cost sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        currency = config_entry.data.get("currency") or config_entry.options.get("currency", "EUR")
        self._attr_native_unit_of_measurement = currency
        self._attr_name = f"Electricity Daily Cost"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_daily_cost"

    @property
    def native_value(self) -> float | None:
        """Return the total cost for today."""
        if self.coordinator.data:
            cost = self.coordinator.data.get("daily_cost", 0.0)
            return round(cost, 4) if cost is not None else None
        return None


class ElectricityMonthlyPriceSensor(
    CoordinatorEntity[CurvesDataUpdateCoordinator], SensorEntity
):
    """Representation of monthly Electricity Cost sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: CurvesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the monthly Electricity Cost sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        currency = config_entry.data.get("currency") or config_entry.options.get("currency", "EUR")
        self._attr_native_unit_of_measurement = currency
        self._attr_name = f"Electricity Monthly Cost"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_monthly_cost"

    @property
    def native_value(self) -> float | None:
        """Return the total cost for this month."""
        if self.coordinator.data:
            cost = self.coordinator.data.get("monthly_cost", 0.0)
            return round(cost, 4) if cost is not None else None
        return None
