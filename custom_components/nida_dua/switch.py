"""Nida Dua — switch platform.

Een schakelaar per dua. Zet je hem aan → dua wordt afgespeeld en de schakelaar
gaat vanzelf na 5 seconden weer uit (zodat hij klaar staat voor de volgende keer).
Handig in bedtijd-automations: zet de schakelaar aan en de dua speelt af.
"""
from __future__ import annotations

import asyncio
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SPEAKER, DOMAIN, DUAS, conf_dua_enabled, conf_dua_sound
from .player import async_play_dua, get_current_volume, get_sound_url

_LOGGER = logging.getLogger(__name__)

AUTO_OFF_DELAY = 5  # seconden


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    opts = entry.options or entry.data
    async_add_entities(
        [
            DuaSwitch(hass, entry, dua_key, meta)
            for dua_key, meta in DUAS.items()
            if opts.get(conf_dua_enabled(dua_key), True)
        ],
        update_before_add=False,
    )


class DuaSwitch(SwitchEntity):
    """Schakelaar om een dua te activeren.

    Aan = dua speelt af. Gaat automatisch na AUTO_OFF_DELAY seconden uit.
    """

    _attr_has_entity_name = True
    _attr_icon = "mdi:hands-pray"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        dua_key: str,
        meta: dict,
    ) -> None:
        self._hass = hass
        self._entry = entry
        self._dua_key = dua_key
        self._meta = meta
        self._attr_unique_id = f"{entry.entry_id}_{dua_key}_switch"
        self._attr_name = f"{meta['name']} schakelaar"
        self._attr_suggested_object_id = f"dua_{dua_key}_schakelaar"
        self._attr_is_on = False

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Nida Dua",
            "manufacturer": "Nida",
            "model": "Dua Player",
        }

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

        opts = self._entry.options or self._entry.data
        speakers = opts.get(CONF_SPEAKER, [])
        volume = get_current_volume(opts)

        filename = opts.get(conf_dua_sound(self._dua_key)) or self._meta["sound"]
        sound_url = get_sound_url(self._hass, filename)
        _LOGGER.debug("Dua switch aan: '%s' op %s", self._dua_key, speakers)
        await async_play_dua(self._hass, speakers, sound_url, volume)

        # Zet schakelaar automatisch terug uit
        async def _auto_off():
            await asyncio.sleep(AUTO_OFF_DELAY)
            self._attr_is_on = False
            self.async_write_ha_state()

        self._hass.async_create_task(_auto_off())

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
