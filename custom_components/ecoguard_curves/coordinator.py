"""Data update coordinator for Curves API."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

# Swedish timezone (Europe/Stockholm)
SWEDISH_TIMEZONE = "Europe/Stockholm"

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
        vat_rate: float = 0.0,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="EcoGuard Curves",
            update_interval=timedelta(seconds=update_interval),
        )
        self.client = client
        self._node_id = node_id
        self._measuring_point_id = measuring_point_id
        self._data_interval = data_interval
        self._vat_rate = vat_rate

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

            # Parse API response structure
            # Response is: [{ "ID": ..., "Name": ..., "Result": [{ "Utl": "ELEC", "Func": "con", "Values": [{ "Time": ..., "Value": ... }] }] }]
            total_consumption = 0.0
            latest_value = 0.0
            latest_timestamp = None
            
            def extract_values(response_data: list[dict[str, Any]], utility: str = "ELEC", func: str = "con") -> list[dict[str, Any]]:
                """Extract values from API response for a specific utility and function."""
                values_list = []
                for item in response_data:
                    if not isinstance(item, dict):
                        continue
                    results = item.get("Result", [])
                    for result in results:
                        if not isinstance(result, dict):
                            continue
                        # Look for specific utility and function (con, price, co2)
                        if result.get("Utl") == utility and result.get("Func") == func:
                            values = result.get("Values", [])
                            if isinstance(values, list):
                                values_list.extend(values)
                return values_list

            # Extract consumption and cost values from response
            # Note: API "price" field actually contains cost per period, not rate
            consumption_values = extract_values(data, "ELEC", "con")
            cost_values = extract_values(data, "ELEC", "price")
            
            # Calculate total consumption and find latest value
            latest_cost_value = 0.0
            latest_cost_timestamp = None
            for point in consumption_values:
                if isinstance(point, dict):
                    value = point.get("Value", 0.0)
                    time_value = point.get("Time")
                    
                    if isinstance(value, (int, float)):
                        total_consumption += float(value)
                        # Track latest value (highest timestamp)
                        if time_value and (latest_timestamp is None or time_value > latest_timestamp):
                            latest_value = float(value)
                            latest_timestamp = time_value
            
            # Find latest cost value (cost for the most recent period)
            for point in cost_values:
                if isinstance(point, dict):
                    value = point.get("Value", 0.0)
                    time_value = point.get("Time")
                    
                    if isinstance(value, (int, float)) and time_value:
                        if latest_cost_timestamp is None or time_value > latest_cost_timestamp:
                            latest_cost_value = float(value)
                            latest_cost_timestamp = time_value

            # Get current day/month/year start in Swedish timezone
            # Convert UTC now to Swedish timezone for proper day boundaries
            import zoneinfo
            from datetime import timezone as dt_timezone
            
            swedish_tz = zoneinfo.ZoneInfo(SWEDISH_TIMEZONE)
            now_utc = dt_util.utcnow()
            
            # Convert UTC to Swedish timezone
            # dt_util.utcnow() returns timezone-aware UTC datetime
            if now_utc.tzinfo is None:
                now_utc = now_utc.replace(tzinfo=dt_timezone.utc)
            
            now_swedish = now_utc.astimezone(swedish_tz)
            
            # Day start in Swedish time (00:00:00)
            day_start_swedish = now_swedish.replace(hour=0, minute=0, second=0, microsecond=0)
            # Convert back to UTC for API calls
            day_start = day_start_swedish.astimezone(dt_timezone.utc)
            
            # Month start in Swedish time
            month_start_swedish = now_swedish.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_start = month_start_swedish.astimezone(dt_timezone.utc)
            
            # Year start in Swedish time
            year_start_swedish = now_swedish.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            year_start = year_start_swedish.astimezone(dt_timezone.utc)

            # Calculate period-specific consumption
            daily_data = await self.client.get_data(
                node_id=self._node_id,
                measuring_point_id=self._measuring_point_id,
                from_date=day_start,
                to_date=now_utc,
                interval=self._data_interval,
            )

            monthly_data = await self.client.get_data(
                node_id=self._node_id,
                measuring_point_id=self._measuring_point_id,
                from_date=month_start,
                to_date=now_utc,
                interval=self._data_interval,
            )

            yearly_data = await self.client.get_data(
                node_id=self._node_id,
                measuring_point_id=self._measuring_point_id,
                from_date=year_start,
                to_date=now_utc,
                interval=self._data_interval,
            )

            # Extract consumption values for daily/monthly/yearly periods
            daily_values = extract_values(daily_data, "ELEC", "con")
            monthly_values = extract_values(monthly_data, "ELEC", "con")
            yearly_values = extract_values(yearly_data, "ELEC", "con")
            
            # Extract cost values for daily/monthly periods
            # API returns cost per period, so we sum to get total cost
            daily_cost_values = extract_values(daily_data, "ELEC", "price")
            monthly_cost_values = extract_values(monthly_data, "ELEC", "price")
            
            # Calculate daily and monthly total costs
            # Each value in the API is already the cost for that period
            daily_cost_without_vat = sum(
                float(p.get("Value", 0.0))
                for p in daily_cost_values
                if isinstance(p, dict) and isinstance(p.get("Value"), (int, float))
            )
            
            monthly_cost_without_vat = sum(
                float(p.get("Value", 0.0))
                for p in monthly_cost_values
                if isinstance(p, dict) and isinstance(p.get("Value"), (int, float))
            )
            
            # Apply VAT if VAT rate is set
            if self._vat_rate > 0:
                vat_multiplier = 1.0 + (self._vat_rate / 100.0)
                daily_cost = daily_cost_without_vat * vat_multiplier
                monthly_cost = monthly_cost_without_vat * vat_multiplier
                latest_cost_value = latest_cost_value * vat_multiplier
            else:
                daily_cost = daily_cost_without_vat
                monthly_cost = monthly_cost_without_vat
            
            daily_consumption = sum(
                float(p.get("Value", 0.0))
                for p in daily_values
                if isinstance(p, dict) and isinstance(p.get("Value"), (int, float))
            )

            monthly_consumption = sum(
                float(p.get("Value", 0.0))
                for p in monthly_values
                if isinstance(p, dict) and isinstance(p.get("Value"), (int, float))
            )

            yearly_consumption = sum(
                float(p.get("Value", 0.0))
                for p in yearly_values
                if isinstance(p, dict) and isinstance(p.get("Value"), (int, float))
            )

            # Format latest reading timestamp as ISO string if available
            latest_reading_str = None
            if latest_timestamp:
                try:
                    # Convert Unix timestamp to datetime
                    latest_dt = dt_util.utc_from_timestamp(latest_timestamp)
                    latest_reading_str = latest_dt.isoformat()
                except (ValueError, TypeError, OSError):
                    # Fallback to Unix timestamp as string if conversion fails
                    latest_reading_str = str(latest_timestamp)
            
            return {
                "consumption": total_consumption,
                "daily_consumption": daily_consumption,
                "monthly_consumption": monthly_consumption,
                "yearly_consumption": yearly_consumption,
                "current_power": latest_value,
                "latest_reading": latest_reading_str,
                "daily_cost": daily_cost,
                "monthly_cost": monthly_cost,
                "current_cost": latest_cost_value,  # Cost for the latest period
            }

        except CurvesAPIError as err:
            raise UpdateFailed(f"Error communicating with Curves API: {err}") from err

