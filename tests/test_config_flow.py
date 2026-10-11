"""Config flow and options."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.components import webhook
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import HomeAssistant
from homeassistant.core_config import async_process_ha_core_config
from homeassistant.data_entry_flow import FlowResultType

from custom_components.drivepulse.const import CONF_LOCAL_ONLY, DOMAIN

from .conftest import WEBHOOK_ID


async def test_flow_creates_the_webhook_and_shows_its_address(
    hass: HomeAssistant,
) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    webhook_id = result["data"][CONF_WEBHOOK_ID]
    assert len(webhook_id) >= 20
    assert f"/api/webhook/{webhook_id}" in result["description_placeholders"]["webhook_url"]
    # No VIN, no account, nothing else is stored.
    assert set(result["data"]) == {CONF_WEBHOOK_ID}


async def test_only_one_entry(hass: HomeAssistant, entry) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_webhook_is_local_only_by_default(hass: HomeAssistant, entry) -> None:
    assert hass.data["webhook"][WEBHOOK_ID]["local_only"] is True
    assert hass.data["webhook"][WEBHOOK_ID]["allowed_methods"] == {"POST"}


async def test_options_switch_off_local_only(hass: HomeAssistant, entry) -> None:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert WEBHOOK_ID in result["description_placeholders"]["webhook_url"]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_LOCAL_ONLY: False}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert hass.data["webhook"][WEBHOOK_ID]["local_only"] is False


async def test_unload_removes_the_webhook(hass: HomeAssistant, entry) -> None:
    assert WEBHOOK_ID in hass.data["webhook"]
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert WEBHOOK_ID not in hass.data["webhook"]


async def test_the_shown_address_is_the_internal_one(hass: HomeAssistant) -> None:
    """With both URLs configured the app is pointed at the LOCAL one."""
    await async_process_ha_core_config(
        hass,
        {
            "internal_url": "http://192.168.1.10:8123",
            "external_url": "https://ha.example.com",
        },
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["description_placeholders"]["webhook_url"].startswith(
        "http://192.168.1.10:8123/api/webhook/"
    )
    entry = result["result"]
    options = await hass.config_entries.options.async_init(entry.entry_id)
    assert options["description_placeholders"]["webhook_url"].startswith(
        "http://192.168.1.10:8123/api/webhook/"
    )
