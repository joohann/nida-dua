"""Nida Dua — config flow."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_SPEAKER, CONF_VOLUME, DEFAULT_SPEAKER, DEFAULT_VOLUME, DOMAIN


def _schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_SPEAKER, default=defaults.get(CONF_SPEAKER, DEFAULT_SPEAKER)): str,
            vol.Required(CONF_VOLUME, default=int(defaults.get(CONF_VOLUME, DEFAULT_VOLUME * 100))): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
        }
    )


class NidaDuaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            speaker = user_input[CONF_SPEAKER].strip()
            if not speaker.startswith("media_player."):
                errors[CONF_SPEAKER] = "invalid_speaker"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Nida Dua", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NidaDuaOptionsFlow(config_entry)


class NidaDuaOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = dict(self._entry.options or self._entry.data)
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
        )
