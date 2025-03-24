"""The LADWP Energy Cost integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the LADWP Energy Cost component from configuration.yaml."""
    _LOGGER.debug("Setting up LADWP Energy Cost from YAML")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LADWP Energy Cost from a config entry."""
    _LOGGER.debug("Setting up LADWP Energy Cost entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    _LOGGER.debug("Forwarding entry setup to platforms: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(update_listener))
    _LOGGER.debug("LADWP Energy Cost entry setup complete")
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug("Reloading LADWP Energy Cost due to options update")
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading LADWP Energy Cost entry: %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("LADWP Energy Cost entry unloaded successfully")
    else:
        _LOGGER.error("Failed to unload LADWP Energy Cost entry")
    
    return unload_ok
