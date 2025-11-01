# Electricity Consumption Integration for Home Assistant

A custom Home Assistant integration that tracks electricity consumption using the [Curves API](https://integration.ecoguard.se/) from EcoGuard.

## Features

- **Real-time consumption tracking**: Monitors electricity consumption from the Curves API
- **Multiple time periods**: Tracks consumption for:
  - Total consumption (cumulative)
  - Daily consumption (current day)
  - Monthly consumption (current month)
  - Yearly consumption (current year)
- **Current power display**: Shows the latest power reading from the API
- **Configurable update interval**: Adjust how often data is fetched from the API (60-3600 seconds)
- **Automatic authentication**: Handles token refresh automatically
- **State persistence**: Consumption values are preserved across Home Assistant restarts

## Installation

### Method 1: Manual Installation (Recommended for Development)

1. Copy the `custom_components/electricity_consumption` folder to your Home Assistant `config` directory:
   ```
   config/
   └── custom_components/
       └── electricity_consumption/
           ├── __init__.py
           ├── api.py
           ├── config_flow.py
           ├── const.py
           ├── coordinator.py
           ├── manifest.json
           └── sensor.py
   ```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "Electricity Consumption" and follow the setup wizard

### Method 2: HACS Installation (Future)

If you plan to publish this integration, you can add it to HACS for easier installation.

## Configuration

The integration uses a config flow, so you can set it up through the Home Assistant UI:

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Electricity Consumption**
4. Enter your Curves API credentials:
   - **Username**: Your Curves API username
   - **Password**: Your Curves API password
   - **Domain Code**: Your domain code from the Curves API
   - **Node ID** (Optional): Specific node ID to monitor
   - **Measuring Point ID** (Optional): Specific measuring point to monitor
   - **Update Interval**: How often to fetch data from the API (60-3600 seconds, default: 300)
   - **Data Interval**: The interval for data aggregation (hour, day, week, month)

### Options

You can adjust the configuration after installation:
1. Go to **Settings** → **Devices & Services**
2. Click on the Electricity Consumption integration
3. Click **Options** to modify:
   - Node ID
   - Measuring Point ID
   - Update interval
   - Data interval

## Usage

After installation, you'll have a new sensor entity that tracks electricity consumption from the Curves API:

- **State**: Total cumulative consumption in kWh
- **Attributes**:
  - `current_power`: Latest power reading in Watts
  - `daily_consumption`: Consumption for the current day in kWh
  - `monthly_consumption`: Consumption for the current month in kWh
  - `yearly_consumption`: Consumption for the current year in kWh
  - `latest_reading`: Timestamp of the latest reading from the API
  - `last_update`: Last successful update from the API

### Example Automations

**Get daily consumption in a notification:**
```yaml
automation:
  - alias: "Daily Electricity Report"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: notify.mobile_app
        data:
          message: >
            Today's electricity consumption: 
            {{ state_attr('sensor.electricity_consumption_curves', 'daily_consumption') }} kWh
```

**Monitor consumption and alert on high usage:**
```yaml
automation:
  - alias: "High Electricity Usage Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_consumption_curves
        above: 100
        for:
          minutes: 30
    action:
      - service: notify.mobile_app
        data:
          message: >
            High electricity consumption detected: 
            {{ states('sensor.electricity_consumption_curves') }} kWh
```

## How It Works

The integration:
1. Authenticates with the Curves API using your credentials
2. Fetches electricity consumption data from the API at regular intervals
3. Calculates consumption for different time periods (daily, monthly, yearly)
4. Automatically refreshes authentication tokens when needed
5. Updates sensor values with the latest data from the API

### API Endpoints Used

The integration uses the following Curves API endpoints:
- `/token` - Authentication
- `/api/{domaincode}/data` - Fetch consumption data
- `/api/{domaincode}/measuringdevices` - List measuring devices
- `/api/{domaincode}/nodes` - List nodes

For more information about the Curves API, visit: https://integration.ecoguard.se/

## Requirements

- Home Assistant 2023.1 or later
- Curves API account with valid credentials
- Internet connection to access the Curves API

## Troubleshooting

**Authentication fails:**
- Verify your username and password are correct
- Check that your domain code is valid
- Ensure your account has API access enabled
- Check Home Assistant logs for detailed error messages

**Sensor shows 0 kWh or no data:**
- Verify your Node ID and Measuring Point ID are correct (if using)
- Check that your account has access to the requested data
- Verify the data interval setting matches available data in the API
- Check Home Assistant logs for API errors

**Consumption not updating:**
- Check the update interval setting (may be too long)
- Verify your internet connection
- Check Home Assistant logs for connectivity or authentication errors
- Ensure the API is accessible from your Home Assistant instance

**Daily/Monthly/Yearly consumption not resetting:**
- These values are calculated from API data based on the configured time ranges
- The integration queries the API for data within each period
- Resets happen automatically based on the current date/time

## API Rate Limits

Be aware that the Curves API may have rate limits. The default update interval of 5 minutes (300 seconds) should be sufficient for most use cases. If you experience rate limiting errors:
- Increase the update interval
- Reduce the frequency of data fetching
- Contact EcoGuard support for rate limit information

## Contributing

This is a custom integration. Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## License

MIT License - feel free to modify and distribute as needed.

## Credits

- Integration powered by the [Curves API](https://integration.ecoguard.se/) from EcoGuard
- Built for Home Assistant
