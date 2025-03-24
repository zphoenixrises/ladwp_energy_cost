"""LADWP Energy Cost Calculator sensor implementation."""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import voluptuous as vol

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_GRID_POWER_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_LOAD_POWER_ENTITY,
    CONF_RATE_PLAN,
    CONF_BILLING_DAY,
    DEFAULT_NAME,
    RATE_PLAN_STANDARD,
    RATE_PLAN_TIME_OF_USE,
    SUMMER_START_MONTH,
    SUMMER_END_MONTH,
    HIGH_PEAK_START,
    HIGH_PEAK_END,
    LOW_PEAK_SUMMER_MORNING_START,
    LOW_PEAK_SUMMER_MORNING_END,
    LOW_PEAK_SUMMER_EVENING_START,
    LOW_PEAK_SUMMER_EVENING_END,
    LOW_PEAK_WINTER_START,
    LOW_PEAK_WINTER_END,
    STANDARD_RATES,
    TOU_RATES,
    TOU_RATES_2024,
    TOU_RATES_2025,
    NET_METERING_CREDIT_RATE,
    STANDARD_RATES_2024,
    STANDARD_RATES_2025,
    TIER1_LIMIT,
    TIER2_LIMIT,
    DEFAULT_ZONE,
    DEFAULT_BILLING_PERIOD,
    TIER_LIMITS,
    CONF_ZONE,
    CONF_BILLING_PERIOD,
)

_LOGGER = logging.getLogger(__name__)

# Constants for sensor data
ATTR_LAST_RESET = "last_reset"
ATTR_HIGH_PEAK_KWH_DELIVERED = "high_peak_kwh_delivered"
ATTR_HIGH_PEAK_KWH_RECEIVED = "high_peak_kwh_received"
ATTR_HIGH_PEAK_KWH_NET = "net_high_peak_kwh"
ATTR_HIGH_PEAK_COST = "high_peak_cost"
ATTR_LOW_PEAK_KWH_DELIVERED = "low_peak_kwh_delivered"
ATTR_LOW_PEAK_KWH_RECEIVED = "low_peak_kwh_received"
ATTR_LOW_PEAK_KWH_NET = "net_low_peak_kwh"
ATTR_LOW_PEAK_COST = "low_peak_cost"
ATTR_BASE_KWH_DELIVERED = "base_kwh_delivered"
ATTR_BASE_KWH_RECEIVED = "base_kwh_received"
ATTR_BASE_KWH_NET = "net_base_kwh"
ATTR_BASE_COST = "base_cost"
ATTR_TOTAL_KWH_DELIVERED = "total_kwh_delivered"
ATTR_TOTAL_KWH_RECEIVED = "total_kwh_received"
ATTR_TOTAL_KWH_NET = "total_kwh_net"

# Solar generation attributes
ATTR_HIGH_PEAK_KWH_GENERATED = "high_peak_kwh_generated"
ATTR_LOW_PEAK_KWH_GENERATED = "low_peak_kwh_generated"
ATTR_BASE_KWH_GENERATED = "base_kwh_generated"
ATTR_TOTAL_KWH_GENERATED = "total_kwh_generated"
ATTR_SOLAR_COST_SAVINGS = "solar_cost_savings"

# Load consumption attributes
ATTR_HIGH_PEAK_KWH_CONSUMED = "high_peak_kwh_consumed"
ATTR_LOW_PEAK_KWH_CONSUMED = "low_peak_kwh_consumed"
ATTR_BASE_KWH_CONSUMED = "base_kwh_consumed"
ATTR_TOTAL_KWH_CONSUMED = "total_kwh_consumed"
ATTR_LOAD_COST = "load_cost"

# Update interval (every minute)
UPDATE_INTERVAL = timedelta(minutes=1)

# Conversion from W to kWh for 1 minute readings
WATTS_TO_KWH_PER_MINUTE = 1 / 60 / 1000  # (60 min/hr * 1000 W/kW)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the LADWP Energy Cost sensor from a config entry."""
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    grid_entity_id = entry.data.get(CONF_GRID_POWER_ENTITY)
    solar_entity_id = entry.data.get(CONF_SOLAR_POWER_ENTITY)
    load_entity_id = entry.data.get(CONF_LOAD_POWER_ENTITY)
    rate_plan = entry.data.get(CONF_RATE_PLAN)
    billing_day = entry.data.get(CONF_BILLING_DAY)
    zone = entry.data.get(CONF_ZONE, DEFAULT_ZONE)
    billing_period = entry.data.get(CONF_BILLING_PERIOD, DEFAULT_BILLING_PERIOD)

    coordinator = LADWPEnergyDataCoordinator(
        hass, name, grid_entity_id, solar_entity_id, load_entity_id, rate_plan, billing_day, zone, billing_period
    )

    # Initial data fetch
    await coordinator.async_config_entry_first_refresh()

    # Create energy cost sensor
    sensors = [
        LADWPEnergyCostSensor(
            coordinator, 
            name, 
            grid_entity_id, 
            solar_entity_id, 
            load_entity_id, 
            rate_plan, 
            billing_day,
            zone,
            billing_period
        )
    ]

    async_add_entities(sensors)


class LADWPEnergyDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching LADWP energy data."""

    def __init__(
        self, 
        hass: HomeAssistant,
        name: str,
        grid_entity_id: str,
        solar_entity_id: Optional[str],
        load_entity_id: Optional[str],
        rate_plan: str,
        billing_day: int,
        zone: str = DEFAULT_ZONE,
        billing_period: str = DEFAULT_BILLING_PERIOD,
    ) -> None:
        """Initialize the data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} coordinator",
            update_interval=UPDATE_INTERVAL,
        )
        self.hass = hass
        self.grid_entity_id = grid_entity_id
        self.solar_entity_id = solar_entity_id
        self.load_entity_id = load_entity_id
        self.rate_plan = rate_plan
        self.billing_day = billing_day
        self.zone = zone
        self.billing_period = billing_period
        
        # Initialize energy data
        self.data = self._init_energy_data()
        
        # Last reset time (billing cycle start)
        self.last_reset = self._get_billing_cycle_start()
        
        # Track when we need to reset counters
        self._unsub_tracking = None

    def _init_energy_data(self) -> Dict[str, Any]:
        """Initialize energy data structure."""
        data = {
            ATTR_HIGH_PEAK_KWH_DELIVERED: 0,
            ATTR_HIGH_PEAK_KWH_RECEIVED: 0,
            ATTR_HIGH_PEAK_KWH_NET: 0,
            ATTR_HIGH_PEAK_COST: 0,
            ATTR_LOW_PEAK_KWH_DELIVERED: 0,
            ATTR_LOW_PEAK_KWH_RECEIVED: 0,
            ATTR_LOW_PEAK_KWH_NET: 0,
            ATTR_LOW_PEAK_COST: 0,
            ATTR_BASE_KWH_DELIVERED: 0,
            ATTR_BASE_KWH_RECEIVED: 0,
            ATTR_BASE_KWH_NET: 0,
            ATTR_BASE_COST: 0,
            ATTR_TOTAL_KWH_DELIVERED: 0,
            ATTR_TOTAL_KWH_RECEIVED: 0,
            ATTR_TOTAL_KWH_NET: 0,
        }
        
        # Add solar data if solar entity provided
        if self.solar_entity_id:
            data.update({
                ATTR_HIGH_PEAK_KWH_GENERATED: 0,
                ATTR_LOW_PEAK_KWH_GENERATED: 0,
                ATTR_BASE_KWH_GENERATED: 0,
                ATTR_TOTAL_KWH_GENERATED: 0,
                ATTR_SOLAR_COST_SAVINGS: 0,
            })
            
        # Add load data if load entity provided
        if self.load_entity_id:
            data.update({
                ATTR_HIGH_PEAK_KWH_CONSUMED: 0,
                ATTR_LOW_PEAK_KWH_CONSUMED: 0,
                ATTR_BASE_KWH_CONSUMED: 0,
                ATTR_TOTAL_KWH_CONSUMED: 0,
                ATTR_LOAD_COST: 0,
            })
            
        return data

    def _get_billing_cycle_start(self) -> datetime:
        """Get the start of the current billing cycle."""
        now = dt_util.now()
        if now.day >= self.billing_day:
            # Current billing cycle started this month
            return dt_util.start_of_local_day(
                datetime(now.year, now.month, self.billing_day)
            )
        else:
            # Current billing cycle started last month
            last_month = now.month - 1 if now.month > 1 else 12
            last_month_year = now.year if now.month > 1 else now.year - 1
            return dt_util.start_of_local_day(
                datetime(last_month_year, last_month, self.billing_day)
            )

    def _is_summer_season(self, date: datetime) -> bool:
        """Check if the date is in the summer season (June-September)."""
        return SUMMER_START_MONTH <= date.month <= SUMMER_END_MONTH

    def _get_time_period(self, date: datetime) -> str:
        """Determine the time period (high_peak, low_peak, base) for the given date."""
        # Weekend is always base period
        if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return "base"
            
        # Get current time without date
        current_time = date.time()
        
        # Check if in summer season (June-September)
        if self._is_summer_season(date):
            # Summer High Peak: 1pm-5pm weekdays
            if HIGH_PEAK_START <= current_time < HIGH_PEAK_END:
                return "high_peak"
            # Summer Low Peak: 10am-1pm, 5pm-8pm weekdays
            elif (LOW_PEAK_SUMMER_MORNING_START <= current_time < LOW_PEAK_SUMMER_MORNING_END or
                  LOW_PEAK_SUMMER_EVENING_START <= current_time < LOW_PEAK_SUMMER_EVENING_END):
                return "low_peak"
            # All other times are base period
            else:
                return "base"
        else:
            # Winter Low Peak: 10am-8pm weekdays
            if LOW_PEAK_WINTER_START <= current_time < LOW_PEAK_WINTER_END:
                return "low_peak"
            # All other times are base period
            else:
                return "base"

    def _get_rate(self, date: datetime, period: str) -> float:
        """Get the rate for the given date and period."""
        # Get current year and month
        year = date.year
        month = date.month
        season = "summer" if self._is_summer_season(date) else "winter"
        
        if self.rate_plan == RATE_PLAN_TIME_OF_USE:
            # Use year-specific rates when available
            if year == 2024:
                # Use 2024 specific rates
                return TOU_RATES_2024[month][period]
            elif year == 2025:
                # Use 2025 specific rates
                return TOU_RATES_2025[month][period]
            else:
                # Fallback to seasonal rates for other years
                # Use latest known rates (2025 for now)
                # First try to get the month-specific rate from the latest year
                if year > 2025:
                    return TOU_RATES_2025[month][period]
                else:
                    # For years before 2024, use the legacy seasonal rates
                    return TOU_RATES[season][period]
        else:
            # For standard rates (R-1A), determine tier based on total usage and zone/billing period
            # Get the total consumption for this billing cycle so far
            total_consumption = self.data[ATTR_TOTAL_KWH_DELIVERED] - self.data[ATTR_TOTAL_KWH_RECEIVED]
            
            # Get tier limits based on zone and billing period
            tier1_limit = TIER_LIMITS[self.zone][self.billing_period]["tier1_limit"]
            tier2_limit = TIER_LIMITS[self.zone][self.billing_period]["tier2_limit"]
            
            # Determine which tier the current usage falls into
            if total_consumption <= tier1_limit:
                tier = "tier1"
            elif total_consumption <= tier2_limit:
                tier = "tier2"
            else:
                tier = "tier3"
                
            # Use year-specific rates when available
            if year == 2024:
                return STANDARD_RATES_2024[month][tier]
            elif year == 2025:
                return STANDARD_RATES_2025[month][tier]
            else:
                # Fallback to seasonal rates for other years
                if year > 2025:
                    return STANDARD_RATES_2025[month][tier]
                else:
                    # For years before 2024, use the legacy seasonal rates
                    return STANDARD_RATES[season][tier]

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update the energy data."""
        now = dt_util.now()
        
        # Check if we need to reset counters
        if now >= self._get_next_reset_time():
            self.data = self._init_energy_data()
            self.last_reset = self._get_billing_cycle_start()
            
        # Get current state of entities
        grid_power = self._get_entity_state(self.grid_entity_id)
        solar_power = self._get_entity_state(self.solar_entity_id) if self.solar_entity_id else None
        load_power = self._get_entity_state(self.load_entity_id) if self.load_entity_id else None
        
        if grid_power is None:
            _LOGGER.error("Cannot get grid power state")
            return self.data
            
        # Determine current time period
        current_period = self._get_time_period(now)
        current_rate = self._get_rate(now, current_period)
        
        # Calculate energy for this update interval (kWh)
        grid_energy = grid_power * WATTS_TO_KWH_PER_MINUTE
        
        # Distribute grid energy to appropriate period
        if grid_energy > 0:  # Delivered from grid (consumption)
            self.data[f"{current_period}_kwh_delivered"] += grid_energy
            self.data[ATTR_TOTAL_KWH_DELIVERED] += grid_energy
        else:  # Received by grid (excess solar)
            received_energy = abs(grid_energy)
            self.data[f"{current_period}_kwh_received"] += received_energy
            self.data[ATTR_TOTAL_KWH_RECEIVED] += received_energy
            
        # Update net values and costs
        for period in ["high_peak", "low_peak", "base"]:
            delivered = self.data[f"{period}_kwh_delivered"]
            received = self.data[f"{period}_kwh_received"]
            net = delivered - received
            
            # Update net values
            self.data[f"net_{period}_kwh"] = net
            
            # Calculate cost for this period
            if net > 0:  # Net consumption
                rate = self._get_rate(now, period)
                self.data[f"{period}_cost"] = net * rate
            else:  # Net production
                # Credit for excess production at net metering rate
                self.data[f"{period}_cost"] = net * NET_METERING_CREDIT_RATE
                
        # Update total net
        self.data[ATTR_TOTAL_KWH_NET] = self.data[ATTR_TOTAL_KWH_DELIVERED] - self.data[ATTR_TOTAL_KWH_RECEIVED]
        
        # Process solar data if available
        if solar_power is not None:
            solar_energy = solar_power * WATTS_TO_KWH_PER_MINUTE
            
            # Add to period solar generation
            self.data[f"{current_period}_kwh_generated"] += solar_energy
            self.data[ATTR_TOTAL_KWH_GENERATED] += solar_energy
            
            # Calculate savings from solar (at current period rate)
            self.data[ATTR_SOLAR_COST_SAVINGS] += solar_energy * current_rate
            
        # Process load data if available
        if load_power is not None:
            load_energy = load_power * WATTS_TO_KWH_PER_MINUTE
            
            # Add to period consumption
            self.data[f"{current_period}_kwh_consumed"] += load_energy
            self.data[ATTR_TOTAL_KWH_CONSUMED] += load_energy
            
            # Calculate load cost (at current period rate)
            self.data[ATTR_LOAD_COST] += load_energy * current_rate
            
        return self.data

    def _get_entity_state(self, entity_id: Optional[str]) -> Optional[float]:
        """Get the current state of an entity as a float."""
        if not entity_id:
            return None
            
        state = self.hass.states.get(entity_id)
        if state is None or state.state == "unknown" or state.state == "unavailable":
            return None
            
        try:
            return float(state.state)
        except (ValueError, TypeError):
            _LOGGER.error("Cannot convert state to float for entity %s: %s", entity_id, state.state)
            return None

    def _get_next_reset_time(self) -> datetime:
        """Get the next time when the cycle should reset."""
        now = dt_util.now()
        if now.day < self.billing_day:
            # Reset will be this month
            return dt_util.start_of_local_day(
                datetime(now.year, now.month, self.billing_day)
            )
        else:
            # Reset will be next month
            next_month = now.month + 1 if now.month < 12 else 1
            next_month_year = now.year if now.month < 12 else now.year + 1
            return dt_util.start_of_local_day(
                datetime(next_month_year, next_month, self.billing_day)
            )


class LADWPEnergyCostSensor(SensorEntity):
    """LADWP Energy Cost Sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = "USD"
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: LADWPEnergyDataCoordinator,
        name: str,
        grid_entity_id: str,
        solar_entity_id: Optional[str],
        load_entity_id: Optional[str],
        rate_plan: str,
        billing_day: int,
        zone: str = DEFAULT_ZONE,
        billing_period: str = DEFAULT_BILLING_PERIOD,
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._name = name
        self._grid_entity_id = grid_entity_id
        self._solar_entity_id = solar_entity_id
        self._load_entity_id = load_entity_id
        self._rate_plan = rate_plan
        self._billing_day = billing_day
        self._zone = zone
        self._billing_period = billing_period
        
        # Entity attributes
        self._attr_name = f"{name} Cost"
        self._attr_unique_id = f"{DOMAIN}_{grid_entity_id}_cost"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> float:
        """Return the state of the sensor (total cost)."""
        return round(sum([
            self.coordinator.data.get(ATTR_HIGH_PEAK_COST, 0),
            self.coordinator.data.get(ATTR_LOW_PEAK_COST, 0),
            self.coordinator.data.get(ATTR_BASE_COST, 0),
        ]), 2)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes of the sensor."""
        attrs = {
            "rate_plan": self._rate_plan,
            "billing_day": self._billing_day,
            "zone": self._zone,
            "billing_period": self._billing_period,
            "last_reset": self.coordinator.last_reset,
        }
        
        # Add all data from coordinator
        attrs.update(self.coordinator.data)
        
        return attrs

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Update the entity."""
        await self.coordinator.async_request_refresh()
