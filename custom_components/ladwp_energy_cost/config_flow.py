"""Config flow for LADWP Energy Cost integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_GRID_POWER_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_LOAD_POWER_ENTITY,
    CONF_RATE_PLAN,
    CONF_BILLING_DAY,
    CONF_ZONE,
    CONF_BILLING_PERIOD,
    DEFAULT_NAME,
    DEFAULT_RATE_PLAN,
    DEFAULT_BILLING_DAY,
    DEFAULT_ZONE,
    DEFAULT_BILLING_PERIOD,
    RATE_PLAN_OPTIONS,
    ZONE_OPTIONS,
    BILLING_PERIOD_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)

class LADWPEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LADWP Energy Cost."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate input
            if not user_input.get(CONF_GRID_POWER_ENTITY):
                errors[CONF_GRID_POWER_ENTITY] = "grid_power_required"
            
            if not errors:
                # Create entry
                return self.async_create_entry(
                    title=user_input.get("name", DEFAULT_NAME),
                    data=user_input,
                )

        # Show the form to the user
        schema = vol.Schema(
            {
                vol.Required("name", default=DEFAULT_NAME): str,
                vol.Required(CONF_GRID_POWER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_SOLAR_POWER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_LOAD_POWER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_RATE_PLAN, default=DEFAULT_RATE_PLAN): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=RATE_PLAN_OPTIONS, translation_key="rate_plan")
                ),
                vol.Required(CONF_ZONE, default=DEFAULT_ZONE): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=ZONE_OPTIONS, translation_key="zone")
                ),
                vol.Required(CONF_BILLING_PERIOD, default=DEFAULT_BILLING_PERIOD): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=BILLING_PERIOD_OPTIONS, translation_key="billing_period")
                ),
                vol.Required(CONF_BILLING_DAY, default=DEFAULT_BILLING_DAY): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=31, mode="slider")
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return LADWPEnergyOptionsFlow(config_entry)


class LADWPEnergyOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the component."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Update entry
            return self.async_create_entry(title="", data=user_input)

        # Fill form with current values or defaults
        current = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_RATE_PLAN,
                    default=current.get(CONF_RATE_PLAN, DEFAULT_RATE_PLAN),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=RATE_PLAN_OPTIONS, translation_key="rate_plan")
                ),
                vol.Required(
                    CONF_ZONE,
                    default=current.get(CONF_ZONE, DEFAULT_ZONE),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=ZONE_OPTIONS, translation_key="zone")
                ),
                vol.Required(
                    CONF_BILLING_PERIOD,
                    default=current.get(CONF_BILLING_PERIOD, DEFAULT_BILLING_PERIOD),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=BILLING_PERIOD_OPTIONS, translation_key="billing_period")
                ),
                vol.Required(
                    CONF_BILLING_DAY,
                    default=current.get(CONF_BILLING_DAY, DEFAULT_BILLING_DAY),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=31, mode="slider")
                ),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=schema, errors=errors
        )
