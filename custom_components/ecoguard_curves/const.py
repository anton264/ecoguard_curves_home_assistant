"""Constants for the EcoGuard Curves integration."""
from typing import Final

DOMAIN: Final = "ecoguard_curves"

# API Configuration
API_BASE_URL: Final = "https://integration.ecoguard.se"
API_TOKEN_ENDPOINT: Final = "/token"
API_DATA_ENDPOINT: Final = "/api/{domaincode}/data"

# Configuration keys
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_DOMAIN_CODE: Final = "domain_code"
CONF_NODE_ID: Final = "node_id"
CONF_MEASURING_POINT_ID: Final = "measuring_point_id"
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_INTERVAL: Final = "interval"  # Data interval (hour, day, etc.)
CONF_CURRENCY: Final = "currency"
CONF_VAT_RATE: Final = "vat_rate"

# Default values
DEFAULT_UPDATE_INTERVAL: Final = 300  # 5 minutes in seconds
DEFAULT_INTERVAL: Final = "hour"
DEFAULT_CURRENCY: Final = "SEK"
DEFAULT_VAT_RATE: Final = 25.0  # 25% VAT default for Sweden

# Attributes
ATTR_CURRENT_POWER: Final = "current_power"
ATTR_DAILY_CONSUMPTION: Final = "daily_consumption"
ATTR_MONTHLY_CONSUMPTION: Final = "monthly_consumption"
ATTR_YEARLY_CONSUMPTION: Final = "yearly_consumption"
ATTR_LATEST_READING: Final = "latest_reading"
ATTR_LAST_UPDATE: Final = "last_update"

# Unit of measurement
UNIT_KWH: Final = "kWh"
UNIT_W: Final = "W"

