"""Nida Dua — config flow."""
from __future__ import annotations

import os

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_EVENING_ENABLED,
    CONF_EVENING_END,
    CONF_EVENING_START,
    CONF_EVENING_VOLUME,
    CONF_SPEAKER,
    CONF_VOLUME,
    DEFAULT_EVENING_END,
    DEFAULT_EVENING_START,
    DEFAULT_EVENING_VOLUME,
    DEFAULT_SPEAKER,
    DEFAULT_VOLUME,
    DOMAIN,
    DUAS,
    conf_dua_enabled,
    conf_dua_sound,
)

_NUM = lambda mn, mx: NumberSelector(NumberSelectorConfig(min=mn, max=mx, step=1, mode=NumberSelectorMode.SLIDER))


def _list_sounds(hass: HomeAssistant) -> list[str]:
    sounds_dir = hass.config.path("www", "nida_dua", "sounds")
    if not os.path.isdir(sounds_dir):
        return []
    return sorted(f for f in os.listdir(sounds_dir) if f.endswith(".mp3"))


def _speakers_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_SPEAKER, default=defaults.get(CONF_SPEAKER, DEFAULT_SPEAKER)): EntitySelector(
                EntitySelectorConfig(domain="media_player", multiple=True)
            ),
            vol.Required(CONF_VOLUME, default=defaults.get(CONF_VOLUME, DEFAULT_VOLUME)): _NUM(0, 100),
            vol.Optional(CONF_EVENING_ENABLED, default=defaults.get(CONF_EVENING_ENABLED, False)): BooleanSelector(),
            vol.Optional(CONF_EVENING_VOLUME, default=defaults.get(CONF_EVENING_VOLUME, DEFAULT_EVENING_VOLUME)): _NUM(0, 100),
            vol.Optional(CONF_EVENING_START, default=defaults.get(CONF_EVENING_START, DEFAULT_EVENING_START)): _NUM(18, 23),
            vol.Optional(CONF_EVENING_END, default=defaults.get(CONF_EVENING_END, DEFAULT_EVENING_END)): _NUM(0, 12),
        }
    )


def _duas_schema(defaults: dict, available_sounds: list[str]) -> vol.Schema:
    sound_options = [SelectOptionDict(value=f, label=f) for f in available_sounds]
    fields: dict = {}
    for key, meta in DUAS.items():
        fields[vol.Optional(conf_dua_enabled(key), default=defaults.get(conf_dua_enabled(key), True))] = BooleanSelector()
        default_sound = meta["sound"]
        options = sound_options if sound_options else [SelectOptionDict(value=default_sound, label=default_sound)]
        fields[vol.Optional(conf_dua_sound(key), default=defaults.get(conf_dua_sound(key), default_sound))] = SelectSelector(
            SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN, custom_value=True)
        )
    return vol.Schema(fields)


class NidaDuaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._data: dict = {}

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_duas()
        return self.async_show_form(step_id="user", data_schema=_speakers_schema({}))

    async def async_step_duas(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Nida Dua", data=self._data)
        available = await self.hass.async_add_executor_job(_list_sounds, self.hass)
        return self.async_show_form(step_id="duas", data_schema=_duas_schema({}, available))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NidaDuaOptionsFlow(config_entry)


class NidaDuaOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry
        self._data: dict = {}

    def _current(self) -> dict:
        return dict(self._entry.options or self._entry.data)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_duas()
        return self.async_show_form(step_id="init", data_schema=_speakers_schema(self._current()))

    async def async_step_duas(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        available = await self.hass.async_add_executor_job(_list_sounds, self.hass)
        return self.async_show_form(step_id="duas", data_schema=_duas_schema(self._current(), available))
