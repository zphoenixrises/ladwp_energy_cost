"""Diagnostics support for LADWP Energy Cost."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_GRID_POWER_ENTITY, CONF_SOLAR_POWER_ENTITY, CONF_LOAD_POWER_ENTITY

TO_REDACT = {CONF_GRID_POWER_ENTITY, CONF_SOLAR_POWER_ENTITY, CONF_LOAD_POWER_ENTITY}

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = {}
    
    # Get integration data
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        data["config"] = async_redact_data(dict(entry.data), TO_REDACT)
        
        # Add entity availability info
        data["entities"] = {}
        for entity_id in [
            entry.data.get(CONF_GRID_POWER_ENTITY),
            entry.data.get(CONF_SOLAR_POWER_ENTITY),
            entry.data.get(CONF_LOAD_POWER_ENTITY),
        ]:
            if entity_id:
                state = hass.states.get(entity_id)
                data["entities"][entity_id] = {
                    "available": state is not None and state.state not in ("unknown", "unavailable"),
                    "state": state.state if state else "not_found",
                }
    
    # Add registered entities from the integration
    data["registered_entities"] = []
    entity_reg = hass.helpers.entity_registry.async_get(hass)
    for entity in entity_reg.entities.values():
        if entity.config_entry_id == entry.entry_id:
            data["registered_entities"].append({
                "entity_id": entity.entity_id,
                "unique_id": entity.unique_id,
                "device_id": entity.device_id,
            })
    
    return data 