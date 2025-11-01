# EcoGuard Curves Integration for Home Assistant

A custom Home Assistant integration that tracks electricity consumption using the [Curves API](https://integration.ecoguard.se/) from EcoGuard. This integration provides real-time monitoring of electricity consumption and costs with support for multiple time periods.

## Features

- **Real-time consumption tracking**: Monitors electricity consumption from the Curves API
- **Multiple time periods**: Tracks consumption for:
  - Total consumption (cumulative)
  - Daily consumption (current day)
  - Monthly consumption (current month)
  - Yearly consumption (current year)
- **Cost tracking**: Monitors electricity costs for current period, daily, and monthly
- **Current power display**: Shows the latest power reading from the API
- **Configurable update interval**: Adjust how often data is fetched from the API (60-3600 seconds)
- **Automatic authentication**: Handles token refresh automatically
- **State persistence**: Consumption values are preserved across Home Assistant restarts

## Prerequisites

Before installing this integration, make sure you have:

- **Home Assistant** 2023.1 or later installed
- A **Curves API account** with valid credentials
- Your **Domain Code** (visible in the URL when logged into Curves, e.g., `HSBBrfBerget`)
- Your **Node ID** (visible in the URL when logged into Curves, e.g., `123`)
- Internet connection to access the Curves API

### Finding Your Credentials

To find your Domain Code and Node ID:

1. Log in to the Curves web interface at  [curves-24.ecoguard.se](https://curves-24.ecoguard.se/)
2. Navigate to your dashboard or node view
3. Check the URL in your browser's address bar
4. The URL will typically look like: `https://curves-24.ecoguard.se/[DOMAIN_CODE]/safetySensors/[NODE_ID]`
   - Example: `https://curves-24.ecoguard.se/HSBBrfBerget/safetySensors/321`
   - In this example:
     - **Domain Code** = `HSBBrfBerget`
     - **Node ID** = `321`

## Installation

### Method 1: Manual Installation (Recommended for Development)

1. **Download or clone** this repository

2. **Copy the integration folder** to your Home Assistant `config` directory:
   ```
   config/
   └── custom_components/
       └── ecoguard_curves/
           ├── __init__.py
           ├── api.py
           ├── config_flow.py
           ├── const.py
           ├── coordinator.py
           ├── manifest.json
           └── sensor.py
   ```

   **For Home Assistant OS/Supervised:**
   - Use the Samba add-on, SSH add-on, or File Editor add-on
   - Navigate to `/config/custom_components/`
   - Create the `ecoguard_curves` folder and copy all files

   **For Home Assistant Container:**
   - Copy files to your mapped `config` directory on the host

3. **Restart Home Assistant** completely (not just reload configuration)

4. **Add the integration:**
   - Go to **Settings** → **Devices & Services** → **Add Integration**
   - Search for **"EcoGuard Curves"**
   - Click on it and follow the setup wizard

### Method 2: HACS Installation (Future)

HACS installation may be available in the future for easier installation.

## Configuration

The integration uses a config flow, so you can set it up entirely through the Home Assistant UI.

### Initial Setup

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **EcoGuard Curves**
4. Click on **EcoGuard Curves** in the results
5. Enter your Curves API credentials:

   | Field | Description | Required | Example |
   |-------|-------------|----------|---------|
   | **Username** | Your Curves API username | Yes | Your login username |
   | **Password** | Your Curves API password | Yes | Your login password |
   | **Domain Code** | Domain code from Curves URL | Yes | `HSBBrfBerget` |
   | **Node ID** | Node ID from Curves URL | Yes | `123` |
   | **Measuring Point ID** | Specific measuring point to monitor | No | `MP001` |
   | **Update Interval** | How often to fetch data (60-3600 seconds) | Yes | `300` (default: 5 minutes) |
   | **Currency** | Currency code for cost values | Yes | `SEK` (default) |

6. Click **Submit**

The integration will:
- Validate your credentials by attempting to authenticate with the Curves API
- Create the sensor entities
- Start fetching data

### Modifying Configuration (Options)

You can adjust the configuration after installation:

1. Go to **Settings** → **Devices & Services**
2. Click on the **EcoGuard Curves** integration
3. Click the **Options** button (or ⋮ menu → **Options**)
4. Modify any of the following:
   - **Node ID** (required)
   - **Measuring Point ID** (optional)
   - **Update Interval** (60-3600 seconds)
   - **Currency** (e.g., SEK, EUR, USD)

## Usage

After installation, the integration creates **6 sensor entities** that track electricity consumption and costs:

### Sensors Created

| Sensor Name | Entity ID Pattern | Description | Unit |
|------------|------------------|-------------|------|
| **Electricity Consumption** | `sensor.electricity_consumption` | Total cumulative consumption | kWh |
| **Electricity Daily Consumption** | `sensor.electricity_daily_consumption` | Daily consumption (current day) | kWh |
| **Electricity Monthly Consumption** | `sensor.electricity_monthly_consumption` | Monthly consumption (current month) | kWh |
| **Electricity Cost** | `sensor.electricity_cost` | Current cost (latest period) | Currency |
| **Electricity Daily Cost** | `sensor.electricity_daily_cost` | Total cost for today | Currency |
| **Electricity Monthly Cost** | `sensor.electricity_monthly_cost` | Total cost for this month | Currency |

### Sensor Attributes

The main **Electricity Consumption** sensor includes additional attributes:
- `current_power`: Current power reading in W
- `latest_reading`: Timestamp of the latest reading
- `last_update`: Last successful update time

### Example Automations

#### Daily Consumption Report

Send a notification every evening with today's consumption:

```yaml
automation:
  - alias: "Daily Electricity Report"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Daily Electricity Report"
          message: >
            Today's consumption: {{ states('sensor.electricity_daily_consumption') }} kWh
            Cost: {{ states('sensor.electricity_daily_cost') }} SEK
```

#### High Usage Alert

Alert when electricity consumption is above a threshold:

```yaml
automation:
  - alias: "High Electricity Usage Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_daily_consumption
        above: 50
        for:
          minutes: 30
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "High Electricity Usage"
          message: >
            High electricity consumption detected: 
            {{ states('sensor.electricity_daily_consumption') }} kWh today
            Current power: {{ state_attr('sensor.electricity_consumption', 'current_power') }} W
```

#### Monthly Cost Summary

Get a summary at the end of each month:

```yaml
automation:
  - alias: "Monthly Electricity Summary"
    trigger:
      - platform: time
        at: "23:59:00"
        day_of_month: -1  # Last day of month
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Monthly Electricity Summary"
          message: >
            Monthly Consumption: {{ states('sensor.electricity_monthly_consumption') }} kWh
            Monthly Cost: {{ states('sensor.electricity_monthly_cost') }} SEK
```

### Lovelace Dashboard Example

Create a simple energy dashboard card:

```yaml
type: entities
entities:
  - entity: sensor.electricity_consumption
    name: Total Consumption
  - entity: sensor.electricity_daily_consumption
    name: Today
  - entity: sensor.electricity_monthly_consumption
    name: This Month
  - entity: sensor.electricity_cost
    name: Current Cost
  - entity: sensor.electricity_daily_cost
    name: Today's Cost
  - entity: sensor.electricity_monthly_cost
    name: Monthly Cost
```

## How It Works

The integration follows this workflow:

1. **Authentication**: Authenticates with the Curves API using your username and password to obtain an access token
2. **Data Fetching**: Fetches electricity consumption data from the API at the configured update interval
3. **Data Processing**: Calculates consumption for different time periods (daily, monthly, yearly) from the raw API data
4. **Token Refresh**: Automatically refreshes authentication tokens when they expire
5. **Sensor Updates**: Updates all sensor entities with the latest data

### API Endpoints Used

The integration uses the following Curves API endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /token` | Authenticate and obtain access token |
| `GET /api/{domaincode}/data` | Fetch consumption data for the specified node |
| `GET /api/{domaincode}/measuringdevices` | List available measuring devices |
| `GET /api/{domaincode}/nodes` | List available nodes |

For more information about the Curves API, visit [integration.ecoguard.se](https://integration.ecoguard.se/)

## Troubleshooting

### Common Issues

#### Authentication Fails

**Symptoms:** Integration fails to set up or stops working with authentication errors.

**Solutions:**
- Verify your username and password are correct
- Check that your domain code matches exactly what's in the URL (case-sensitive)
- Ensure your account has API access enabled
- Check Home Assistant logs for detailed error messages:
  - Go to **Settings** → **System** → **Logs**
  - Look for errors containing `ecoguard_curves` or `CurvesAPIError`

#### Sensor Shows 0 kWh or No Data

**Symptoms:** Sensors are created but show 0 kWh or `unknown` state.

**Solutions:**
- Verify your **Node ID** is correct (this is now required)
- Check that your account has access to the requested node
- Verify the **Measuring Point ID** is correct (if using)
- Ensure data is available in the Curves API for your node
- Check Home Assistant logs for API errors
- Try increasing the update interval to see if data appears after a longer wait

#### Consumption Not Updating

**Symptoms:** Sensors are created but values don't change.

**Solutions:**
- Check the **Update Interval** setting (default is 300 seconds / 5 minutes)
  - If it's too long, decrease it (minimum 60 seconds)
  - Very short intervals may hit rate limits
- Verify your internet connection
- Check Home Assistant logs for connectivity or authentication errors
- Ensure the API is accessible from your Home Assistant instance
- Try restarting Home Assistant to reinitialize the integration

#### Daily/Monthly Consumption Not Resetting

**Symptoms:** Daily or monthly values don't reset at midnight or month start.

**Explanation:**
- These values are calculated from API data based on the configured time ranges
- The integration queries the API for data within each period
- Resets happen automatically based on the current date/time in Swedish timezone (Europe/Stockholm)
- If values don't reset immediately, wait a few minutes after midnight/month start

#### Integration Disappears After Restart

**Symptoms:** Integration is removed after Home Assistant restart.

**Solutions:**
- Ensure all files are correctly copied to `config/custom_components/ecoguard_curves/`
- Verify the `manifest.json` file exists and is valid
- Check Home Assistant logs for import errors
- Make sure Home Assistant version is 2023.1 or later

### Getting Help

If you're still experiencing issues:

1. **Check Logs**: Review Home Assistant logs for detailed error messages
   - Go to **Settings** → **System** → **Logs**
   - Filter for `ecoguard_curves`

2. **Verify Configuration**: Double-check all credentials and IDs match what's in the Curves URL

3. **Test API Access**: Verify you can log in to the Curves web interface with your credentials

4. **Report Issues**: If you find a bug or have a feature request, please report it on the repository's issue tracker

## API Rate Limits

Be aware that the Curves API may have rate limits. The default update interval of **5 minutes (300 seconds)** should be sufficient for most use cases.

If you experience rate limiting errors:
- **Increase the update interval** (e.g., to 600 seconds / 10 minutes)
- Reduce the frequency of data fetching
- Contact EcoGuard support for specific rate limit information

**Recommendation:** Start with the default 300 seconds and only decrease if you need more frequent updates. Very short intervals (< 120 seconds) may cause issues.

## Requirements

- **Home Assistant**: 2023.1 or later
- **Python**: 3.10 or later (handled by Home Assistant)
- **Network**: Internet connection to access `integration.ecoguard.se`
- **Account**: Valid Curves API account with access credentials

## Development

This is a custom integration developed for Home Assistant. The integration structure follows Home Assistant's best practices:

- Uses config flow for setup
- Implements DataUpdateCoordinator for efficient data updates
- Follows Home Assistant entity naming conventions
- Supports options flow for configuration updates

### File Structure

```
custom_components/ecoguard_curves/
├── __init__.py          # Integration setup and entry handling
├── api.py               # Curves API client implementation
├── config_flow.py       # Configuration flow and options flow
├── const.py             # Constants and default values
├── coordinator.py       # Data update coordinator
├── manifest.json        # Integration manifest and metadata
└── sensor.py            # Sensor entity implementations
```

## Contributing

Contributions are welcome! This is a custom integration, and we encourage:

- **Reporting issues**: Found a bug? Please report it with detailed information
- **Suggesting improvements**: Have ideas for new features or improvements?
- **Submitting pull requests**: Implemented a fix or feature? Submit a PR!

When contributing:
- Follow Home Assistant's coding standards
- Include appropriate error handling
- Add comments for complex logic
- Test your changes thoroughly

## License

MIT License - feel free to modify and distribute as needed.

## Credits

- Integration powered by the [Curves API](https://integration.ecoguard.se/) from EcoGuard
- Built for Home Assistant
- Developed for tracking electricity consumption and costs

---

**Note:** This integration is not officially supported by EcoGuard. It is a community-maintained custom integration for Home Assistant.