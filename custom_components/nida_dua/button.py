"""Nida Dua — button platform.

Elke dua krijgt een Button-entiteit. Druk op de knop → dua wordt afgespeeld.
"""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SPEAKER, DOMAIN, DUAS, conf_dua_enabled
from .player import async_play_dua, get_current_volume, get_sound_url

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    opts = entry.options or entry.data
    async_add_entities(
        [
            DuaButton(hass, entry, dua_key, meta)
            for dua_key, meta in DUAS.items()
            if opts.get(conf_dua_enabled(dua_key), True)
        ],
        update_before_add=False,
    )


class DuaButton(ButtonEntity):
    """Knop om een specifieke dua af te spelen."""

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
        self._attr_unique_id = f"{entry.entry_id}_{dua_key}_button"
        self._attr_name = meta["name"]
        self._attr_suggested_object_id = f"dua_{dua_key}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Nida Dua",
            "manufacturer": "Nida",
            "model": "Dua Player",
        }

    async def async_press(self) -> None:
        """Speel de dua af."""
        opts = self._entry.options or self._entry.data
        speakers = opts.get(CONF_SPEAKER, [])
        volume = get_current_volume(opts)

        sound_url = get_sound_url(self._hass, self._meta["sound"])
        _LOGGER.debug("Speel dua '%s' af op %s (volume %.2f)", self._dua_key, speakers, volume)
        await async_play_dua(self._hass, speakers, sound_url, volume)
