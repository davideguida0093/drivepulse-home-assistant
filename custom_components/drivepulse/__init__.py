"""The DrivePulse integration: sensors and trip events from the DrivePulse app.

The app POSTs JSON to a webhook of this Home Assistant (nothing leaves the
house, no cloud, no account). This integration creates the webhook, one device
per vehicle and the sensors, so no YAML is needed.
"""

from __future__ import annotations

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_WEBHOOK_ID, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_LOCAL_ONLY, DEFAULT_LOCAL_ONLY, DOMAIN
from .hub import DrivePulseHub

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

type DrivePulseConfigEntry = ConfigEntry[DrivePulseHub]


async def async_setup_entry(hass: HomeAssistant, entry: DrivePulseConfigEntry) -> bool:
    """Register the webhook and create the entities."""
    hub = DrivePulseHub(hass, entry)
    await hub.async_load()
    for vehicle in hub.vehicles.values():
        hub.ensure_device(vehicle)
    entry.runtime_data = hub

    webhook.async_register(
        hass,
        DOMAIN,
        "DrivePulse",
        entry.data[CONF_WEBHOOK_ID],
        hub.handle_webhook,
        local_only=entry.options.get(CONF_LOCAL_ONLY, DEFAULT_LOCAL_ONLY),
        allowed_methods=["POST"],
    )
    entry.async_on_unload(
        lambda: webhook.async_unregister(hass, entry.data[CONF_WEBHOOK_ID])
    )
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """The webhook is registered with the option: reload to apply a change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: DrivePulseConfigEntry) -> bool:
    """Save what is waiting, then unload."""
    await entry.runtime_data.async_flush()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: DrivePulseConfigEntry) -> None:
    """Forget the saved vehicles of a removed integration."""
    await DrivePulseHub(hass, entry).async_remove_storage()
