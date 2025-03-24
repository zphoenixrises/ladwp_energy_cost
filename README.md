# LADWP Energy Cost Calculator

A Home Assistant integration to calculate electricity costs for LADWP customers in Los Angeles.

## Features

- Calculates electricity costs based on LADWP rate plans
- Supports both Standard and Time-of-Use (TOU) rate plans
- Customizable billing cycle and zone settings
- Works with grid power, solar power, and load power entities

## Installation

### HACS Installation (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS
3. Install the integration through HACS
4. Restart Home Assistant
5. Add the integration through the HA Configuration -> Integrations menu

### Manual Installation

1. Copy the `custom_components/ladwp_energy_cost` directory to your Home Assistant configuration directory
2. Restart Home Assistant
3. Add the integration through the HA Configuration -> Integrations menu

## Configuration

After adding the integration, you will need to configure:

1. Grid power entity (required) - The entity that measures your grid power in watts
2. Solar power entity (optional) - The entity that measures your solar production in watts
3. Load power entity (optional) - The entity that measures your total consumption in watts
4. Rate plan - Standard or Time-of-Use
5. Billing day - The day of the month your billing cycle starts
6. Zone - Your LADWP zone (affects tier limits)
7. Billing period - Monthly or bimonthly billing

## License

This project is licensed under the MIT License. 