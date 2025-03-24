"""Constants for the LADWP Energy Cost Calculator integration."""
from datetime import time
import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_ENTITY_ID

DOMAIN = "ladwp_energy_cost"

# Configuration constants
CONF_GRID_POWER_ENTITY = "grid_power_entity"
CONF_SOLAR_POWER_ENTITY = "solar_power_entity"
CONF_LOAD_POWER_ENTITY = "load_power_entity"
CONF_RATE_PLAN = "rate_plan"
CONF_BILLING_DAY = "billing_day"
CONF_ZONE = "zone"
CONF_BILLING_PERIOD = "billing_period"

# Rate plan options
RATE_PLAN_STANDARD = "standard"
RATE_PLAN_TIME_OF_USE = "time_of_use"
RATE_PLAN_OPTIONS = [RATE_PLAN_STANDARD, RATE_PLAN_TIME_OF_USE]

# Zone options
ZONE_1 = "zone_1"
ZONE_2 = "zone_2"
ZONE_OPTIONS = [ZONE_1, ZONE_2]

# Billing period options
BILLING_MONTHLY = "monthly"
BILLING_BIMONTHLY = "bimonthly"
BILLING_PERIOD_OPTIONS = [BILLING_MONTHLY, BILLING_BIMONTHLY]

# Default values
DEFAULT_NAME = "LADWP Energy Cost"
DEFAULT_RATE_PLAN = RATE_PLAN_TIME_OF_USE
DEFAULT_BILLING_DAY = 1
DEFAULT_ZONE = ZONE_1
DEFAULT_BILLING_PERIOD = BILLING_MONTHLY

# LADWP Time of Use (R-1B) Time Periods
# High Peak: 1pm-5pm weekdays (June-Sep)
# Low Peak: 10am-1pm, 5pm-8pm weekdays (June-Sep), 10am-8pm weekdays (Oct-May)
# Base: All other times

# Season periods
SUMMER_START_MONTH = 6   # June
SUMMER_END_MONTH = 9     # September

# Define time periods for TOU
HIGH_PEAK_START = time(13, 0)  # 1:00 PM
HIGH_PEAK_END = time(17, 0)    # 5:00 PM

LOW_PEAK_SUMMER_MORNING_START = time(10, 0)   # 10:00 AM
LOW_PEAK_SUMMER_MORNING_END = time(13, 0)     # 1:00 PM
LOW_PEAK_SUMMER_EVENING_START = time(17, 0)   # 5:00 PM
LOW_PEAK_SUMMER_EVENING_END = time(20, 0)     # 8:00 PM

LOW_PEAK_WINTER_START = time(10, 0)           # 10:00 AM
LOW_PEAK_WINTER_END = time(20, 0)             # 8:00 PM

# Tier limits based on zone and billing period
TIER_LIMITS = {
    ZONE_1: {
        BILLING_MONTHLY: {
            "tier1_limit": 350,   # First 350 kWh
            "tier2_limit": 1050,  # Next 700 kWh (350+700=1050)
        },
        BILLING_BIMONTHLY: {
            "tier1_limit": 700,   # First 700 kWh
            "tier2_limit": 2100,  # Next 1400 kWh (700+1400=2100)
        },
    },
    ZONE_2: {
        BILLING_MONTHLY: {
            "tier1_limit": 500,   # First 500 kWh
            "tier2_limit": 1500,  # Next 1000 kWh (500+1000=1500)
        },
        BILLING_BIMONTHLY: {
            "tier1_limit": 1000,  # First 1000 kWh
            "tier2_limit": 3000,  # Next 2000 kWh (1000+2000=3000)
        },
    },
}

# Standard Residential (R-1A) Rates
# These values include all adjustment factors
# Legacy tier limits (for backward compatibility)
TIER1_LIMIT = 350  # kWh (Zone 1 Monthly)
TIER2_LIMIT = 1050  # kWh (Zone 1 Monthly)

# Updated with accurate monthly rates from LADWP
# Format: Year -> Month -> Tier
STANDARD_RATES_2024 = {
    # January - March
    1: {"tier1": 0.20042, "tier2": 0.25901, "tier3": 0.25901},
    2: {"tier1": 0.20042, "tier2": 0.25901, "tier3": 0.25901},
    3: {"tier1": 0.20042, "tier2": 0.25901, "tier3": 0.25901},
    # April - May
    4: {"tier1": 0.19645, "tier2": 0.25504, "tier3": 0.25504},
    5: {"tier1": 0.19645, "tier2": 0.25504, "tier3": 0.25504},
    # June
    6: {"tier1": 0.19645, "tier2": 0.25504, "tier3": 0.34205},
    # July - September
    7: {"tier1": 0.21169, "tier2": 0.27028, "tier3": 0.35729},
    8: {"tier1": 0.21169, "tier2": 0.27028, "tier3": 0.35729},
    9: {"tier1": 0.21169, "tier2": 0.27028, "tier3": 0.35729},
    # October - December
    10: {"tier1": 0.21408, "tier2": 0.27267, "tier3": 0.27267},
    11: {"tier1": 0.21408, "tier2": 0.27267, "tier3": 0.27267},
    12: {"tier1": 0.21408, "tier2": 0.27267, "tier3": 0.27267},
}

STANDARD_RATES_2025 = {
    # January - March
    1: {"tier1": 0.22296, "tier2": 0.28155, "tier3": 0.28155},
    2: {"tier1": 0.22296, "tier2": 0.28155, "tier3": 0.28155},
    3: {"tier1": 0.22296, "tier2": 0.28155, "tier3": 0.28155},
    # April - May
    4: {"tier1": 0.22765, "tier2": 0.28624, "tier3": 0.28624},
    5: {"tier1": 0.22765, "tier2": 0.28624, "tier3": 0.28624},
    # June
    6: {"tier1": 0.22765, "tier2": 0.28624, "tier3": 0.37325},
    # July - September (using June rates as placeholder until actual rates are available)
    7: {"tier1": 0.22765, "tier2": 0.28624, "tier3": 0.37325},
    8: {"tier1": 0.22765, "tier2": 0.28624, "tier3": 0.37325},
    9: {"tier1": 0.22765, "tier2": 0.28624, "tier3": 0.37325},
    # October - December (using previous year's rates as placeholder)
    10: {"tier1": 0.21408, "tier2": 0.27267, "tier3": 0.27267},
    11: {"tier1": 0.21408, "tier2": 0.27267, "tier3": 0.27267},
    12: {"tier1": 0.21408, "tier2": 0.27267, "tier3": 0.27267},
}

# For backward compatibility, maintain the old format as well
STANDARD_RATES = {
    "summer": {  # June-September
        "tier1": 0.21169,  # Tier 1 (0-350 kWh)
        "tier2": 0.27028,  # Tier 2 (351-1050 kWh)
        "tier3": 0.35729,  # Tier 3 (>1050 kWh)
    },
    "winter": {  # October-May
        "tier1": 0.20042,  # Tier 1 (0-350 kWh)
        "tier2": 0.25901,  # Tier 2 (351-1050 kWh)
        "tier3": 0.25901,  # Tier 3 (>1050 kWh)
    },
    "tier1_limit": TIER1_LIMIT,
    "tier2_limit": TIER2_LIMIT,
}

# Time of Use (R-1B) Rates
# Updated with accurate monthly rates from LADWP
# Format: Year -> Month -> Rate Type
TOU_RATES_2024 = {
    # January - March
    1: {"high_peak": 0.22918, "low_peak": 0.22918, "base": 0.20564},
    2: {"high_peak": 0.22918, "low_peak": 0.22918, "base": 0.20564},
    3: {"high_peak": 0.22918, "low_peak": 0.22918, "base": 0.20564},
    # April - May
    4: {"high_peak": 0.22521, "low_peak": 0.22521, "base": 0.20167},
    5: {"high_peak": 0.22521, "low_peak": 0.22521, "base": 0.20167},
    # June
    6: {"high_peak": 0.28361, "low_peak": 0.22521, "base": 0.19777},
    # July - September
    7: {"high_peak": 0.29885, "low_peak": 0.24045, "base": 0.21301},
    8: {"high_peak": 0.29885, "low_peak": 0.24045, "base": 0.21301},
    9: {"high_peak": 0.29885, "low_peak": 0.24045, "base": 0.21301},
    # October - December
    10: {"high_peak": 0.24284, "low_peak": 0.24284, "base": 0.21930},
    11: {"high_peak": 0.24284, "low_peak": 0.24284, "base": 0.21930},
    12: {"high_peak": 0.24284, "low_peak": 0.24284, "base": 0.21930},
}

TOU_RATES_2025 = {
    # January - March
    1: {"high_peak": 0.25172, "low_peak": 0.25172, "base": 0.22818},
    2: {"high_peak": 0.25172, "low_peak": 0.25172, "base": 0.22818},
    3: {"high_peak": 0.25172, "low_peak": 0.25172, "base": 0.22818},
    # April - May
    4: {"high_peak": 0.25641, "low_peak": 0.25641, "base": 0.23287},
    5: {"high_peak": 0.25641, "low_peak": 0.25641, "base": 0.23287},
    # June
    6: {"high_peak": 0.31481, "low_peak": 0.25641, "base": 0.22897},
    # July - September (using June rates as placeholder until actual rates are available)
    7: {"high_peak": 0.31481, "low_peak": 0.25641, "base": 0.22897},
    8: {"high_peak": 0.31481, "low_peak": 0.25641, "base": 0.22897},
    9: {"high_peak": 0.31481, "low_peak": 0.25641, "base": 0.22897},
    # October - December (using previous year's rates as placeholder)
    10: {"high_peak": 0.24284, "low_peak": 0.24284, "base": 0.21930},
    11: {"high_peak": 0.24284, "low_peak": 0.24284, "base": 0.21930},
    12: {"high_peak": 0.24284, "low_peak": 0.24284, "base": 0.21930},
}

# For backward compatibility, maintain the old format as well
TOU_RATES = {
    "winter": {  # January-May, October-December
        "high_peak": 0.22918,
        "low_peak": 0.22918,
        "base": 0.20564,
    },
    "summer": {  # June-September
        "high_peak": 0.29885,
        "low_peak": 0.24045,
        "base": 0.21301,
    },
}

# Net Metering Credit Rate (when sending power back to grid)
# Using the base rate for simplicity
NET_METERING_CREDIT_RATE = 0.1974
