"""Data update coordinator for Curves API."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .api import CurvesAPIClient, CurvesAPIError
from .const import DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class CurvesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Curves API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: CurvesAPIClient,
        node_id: str | None,
        measuring_point_id: str | None,
        update_interval: int,
        data_interval: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Curves Electricity Consumption",
            update_interval=timedelta(seconds=update_interval),
        )
        self.client = client
        self._node_id = node_id
        self._measuring_point_id = measuring_point_id
        self._data_interval = data_interval

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Curves API."""
        try:
            # Get data for the last 24 hours to calculate consumption
            to_date = dt_util.utcnow()
            from_date = to_date - timedelta(days=1)

            # Get hourly data for consumption tracking
            data = await self.client.get_data(
                node_id=self._node_id,
                measuring_point_id=self._measuring_point_id,
                from_date=from_date,
                to_date=to_date,
                interval=self._data_interval,
            )

            if not data:
                _LOGGER.warning("No data received from Curves API")
                return {
                    "consumption": 0.0,
                    "daily_consumption": 0.0,
                    "monthly_consumption": 0.0,
                    "yearly_consumption": 0.0,
                    "current_power": 0.0,
                    "latest_reading": None,
                }

            # Calculate consumption from data points
            # Data format depends on API response, typically contains timestamp and value
            total_consumption = 0.0
            latest_value = 0.0
            latest_timestamp = None

            # Parse data points - adjust based on actual API response format
            for point in data:
                if isinstance(point, dict):
                    # Try different possible field names for value
                    value = (
                        point.get("value")
                        or point.get("consumption")
                        or point.get("energy")
                        or 0.0
                    )
                    timestamp_str = point.get("timestamp") or point.get("time") or point.get("date")
                    
                    if isinstance(value, (int, float)):
                        total_consumption += float(value)
                        latest_value = float(value)
                        if timestamp_str:
                            latest_timestamp = timestamp_str

            # Get current day start
            now = dt_util.utcnow()
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

            # Calculate period-specific consumption
            daily_data = await self.client.get_data(
                node_id=self._node_id,
                measuring_point_id=self._measuring_point_id,
                from_date=day_start,
                to_date=now,
                interval=self._data_interval,
            )

            monthly_data = await self.client.get_data(
                node_id=self._node_id,
                measuring_point_id=self._measuring_point_id,
                from_date=month_start,
                to_date=now,
                interval=self._data_interval,
            )

            yearly_data = await self.client.get_data(
                node_id=self._node_id,
                measuring_point_id=self._measuring_point_id,
                from_date=year_start,
                to_date=now,
                interval=self._data_interval,
            )

            daily_consumption = sum(
                float(p.get("value") or p.get("consumption") or p.get("energy") or 0.0)
                for p in (daily_data if isinstance(daily_data, list) else [daily_data])
                if isinstance(p, dict)
            )

            monthly_consumption = sum(
                float(p.get("value") or p.get("consumption") or p.get("energy") or 0.0)
                for p in (monthly_data if isinstance(monthly_data, list) else [monthly_data])
                if isinstance(p, dict)
            )

            yearly_consumption = sum(
                float(p.get("value") or p.get("consumption") or p.get("energy") or 0.0)
                for p in (yearly_data if isinstance(yearly_data, list) else [yearly_data])
                if isinstance(p, dict)
            )

            return {
                "consumption": total_consumption,
                "daily_consumption": daily_consumption,
                "monthly_consumption": monthly_consumption,
                "yearly_consumption": yearly_consumption,
                "current_power": latest_value,
                "latest_reading": latest_timestamp,
            }

        except CurvesAPIError as err:
            raise UpdateFailed(f"Error communicating with Curves API: {err}") from err

