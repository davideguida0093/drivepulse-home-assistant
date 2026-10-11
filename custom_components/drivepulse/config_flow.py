"""Config flow: one click creates the webhook and shows its address."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import webhook
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.network import NoURLAvailableError

from .const import CONF_LOCAL_ONLY, DEFAULT_LOCAL_ONLY, DOMAIN


def webhook_address(hass: HomeAssistant, webhook_id: str) -> str:
    """The address to paste in the app: the local one if Home Assistant has it."""
    try:
        return webhook.async_generate_url(
            hass, webhook_id, allow_external=False, allow_ip=True
        )
    except NoURLAvailableError:
        return f"http://homeassistant.local:8123/api/webhook/{webhook_id}"


class DrivePulseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add DrivePulse: no questions, the webhook is generated."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
        webhook_id = webhook.async_generate_id()
        return self.async_create_entry(
            title="DrivePulse",
            data={CONF_WEBHOOK_ID: webhook_id},
            description_placeholders={
                "webhook_url": webhook_address(self.hass, webhook_id)
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return DrivePulseOptionsFlow()


class DrivePulseOptionsFlow(OptionsFlow):
    """Show the webhook address again, and the local-only switch."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LOCAL_ONLY,
                        default=self.config_entry.options.get(
                            CONF_LOCAL_ONLY, DEFAULT_LOCAL_ONLY
                        ),
                    ): bool
                }
            ),
            description_placeholders={
                "webhook_url": webhook_address(
                    self.hass, self.config_entry.data[CONF_WEBHOOK_ID]
                )
            },
        )
