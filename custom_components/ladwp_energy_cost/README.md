# LADWP Energy Cost Calculator

This custom integration for Home Assistant calculates electricity costs for LADWP (Los Angeles Department of Water and Power) customers based on their usage patterns and rate plan.

## Features

- Supports both Standard Residential (R-1A) and Time of Use (R-1B) rate plans
- Tracks energy consumption by time period (High Peak, Low Peak, Base)
- Calculates costs accurately based on LADWP's 2024 and 2025 rate structure
- Monthly-specific rates for more accurate calculations
- Supports Zone 1 and Zone 2 service areas
- Compatible with both monthly and bi-monthly billing periods
- Optional tracking of solar generation and home consumption
- Compatible with net metering
- Resets metrics on your billing cycle date

## Requirements

- Home Assistant
- At least one power sensor for grid power (in watts)
- Optional: Solar production sensor (in watts)
- Optional: Home load/consumption sensor (in watts)

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add the URL: `https://github.com/zphoenixrises/ladwp_energy_cost`
   - Category: Integration
3. Click "Install" and follow the installation steps
4. Restart Home Assistant

### Manual

1. Download this repository
2. Copy the `custom_components/ladwp_energy_cost` folder to your Home Assistant `config/custom_components` directory
3. Restart Home Assistant

## Configuration

1. In Home Assistant, go to **Settings** > **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for "LADWP Energy Cost"
4. Follow the configuration steps:
   - **Grid Power Entity:** Select your grid power sensor (required)
   - **Solar Power Entity:** Select your solar power sensor (optional)
   - **Load Power Entity:** Select your home load power sensor (optional)
   - **Rate Plan:** Choose between Standard Residential (R-1A) or Time of Use (R-1B)
   - **Service Zone:** Select Zone 1 or Zone 2 (affects tier limits)
   - **Billing Period:** Select Monthly or Bi-Monthly (affects tier limits)
   - **Billing Day:** Set the day of the month when your billing cycle starts

## Understanding the Data

### Grid Power Only Configuration

When only grid power is provided, the sensor will show:
- **High Peak kWh Delivered/Received/Net:** Energy from/to grid during High Peak hours
- **Low Peak kWh Delivered/Received/Net:** Energy from/to grid during Low Peak hours
- **Base kWh Delivered/Received/Net:** Energy from/to grid during Base hours
- **Costs for each period and total**

### With Solar Power Sensor

When a solar power sensor is added, you'll also see:
- **High/Low/Base Peak kWh Generated:** Solar energy generated during each period
- **Total kWh Generated:** Total solar energy generated
- **Solar Cost Savings:** Estimated savings from solar generation

### With Load Power Sensor

When a load power sensor is added, you'll also see:
- **High/Low/Base Peak kWh Consumed:** Home energy consumption during each period
- **Total kWh Consumed:** Total home energy consumption
- **Load Cost:** Estimated cost of total consumption

## Rate Information

This integration uses LADWP's accurate electricity rates from:
https://www.ladwp.com/account/customer-service/electric-rates/residential-rates

### LADWP Service Zones and Tier Limits

LADWP has different tier limits based on your service zone and billing period:

| | Zone 1 | | Zone 2 | |
|---|---|---|---|---|
| | Monthly | Bi-Monthly | Monthly | Bi-Monthly |
| Tier 1 | First 350 kWh | First 700 kWh | First 500 kWh | First 1,000 kWh |
| Tier 2 | Next 700 kWh | Next 1,400 kWh | Next 1,000 kWh | Next 2,000 kWh |
| Tier 3 | Above 1,050 kWh | Above 2,100 kWh | Above 1,500 kWh | Above 3,000 kWh |

### Standard Residential (R-1A) 2024 Rates

| Period | Tier 1 | Tier 2 | Tier 3 |
|--------|-------------------|---------------------|-------------------|
| January - March | $0.20042 | $0.25901 | $0.25901 |
| April - May | $0.19645 | $0.25504 | $0.25504 |
| June | $0.19645 | $0.25504 | $0.34205 |
| July - September | $0.21169 | $0.27028 | $0.35729 |
| October - December | $0.21408 | $0.27267 | $0.27267 |

### Standard Residential (R-1A) 2025 Rates (partial)

| Period | Tier 1 | Tier 2 | Tier 3 |
|--------|-------------------|---------------------|-------------------|
| January - March | $0.22296 | $0.28155 | $0.28155 |
| April - May | $0.22765 | $0.28624 | $0.28624 |
| June | $0.22765 | $0.28624 | $0.37325 |

The integration also includes estimates for July-December 2025 based on previous patterns.

### Time of Use (R-1B) 2024 Rates

| Period | High Peak | Low Peak | Base |
|--------|-----------|----------|------|
| January - March | $0.22918 | $0.22918 | $0.20564 |
| April - May | $0.22521 | $0.22521 | $0.20167 |
| June | $0.28361 | $0.22521 | $0.19777 |
| July - September | $0.29885 | $0.24045 | $0.21301 |
| October - December | $0.24284 | $0.24284 | $0.21930 |

### Time of Use (R-1B) 2025 Rates (partial)

| Period | High Peak | Low Peak | Base |
|--------|-----------|----------|------|
| January - March | $0.25172 | $0.25172 | $0.22818 |
| April - May | $0.25641 | $0.25641 | $0.23287 |
| June | $0.31481 | $0.25641 | $0.22897 |

### Time Periods for Time of Use (R-1B)

- **High Peak:** 1pm-5pm weekdays (June-September only)
- **Low Peak:** 
  - Summer (Jun-Sep): 10am-1pm, 5pm-8pm weekdays
  - Winter (Oct-May): 10am-8pm weekdays
- **Base:** All other times (including weekends and holidays)

## Troubleshooting

- Make sure your power sensors are reporting in watts (W), not kilowatts (kW)
- The sensor updates every minute to track energy usage accurately
- Billing cycle resets happen at midnight on your billing day
- Verify your service zone by checking your LADWP bill or contacting customer service
- If you're not sure about your billing period, check your LADWP bill - it will indicate if you're on monthly or bi-monthly billing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This integration is licensed under MIT License. 