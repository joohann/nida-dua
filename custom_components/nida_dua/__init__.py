"""Nida Dua — Islamic supplication (dua) player for Home Assistant.

Platforms:
  - button   → druk om dua direct af te spelen
  - switch   → zet aan om dua af te spelen (gaat automatisch uit)

Sounds staan in: www/nida_dua/sounds/
Kopieer je MP3-bestanden naar /config/www/nida_dua/sounds/ in Home Assistant.
"""
from __future__ import annotations

import logging
import os
import shutil

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["button", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.async_add_executor_job(_copy_sounds, hass, os.path.dirname(__file__))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _copy_sounds(hass: HomeAssistant, component_dir: str) -> None:
    """Kopieer gebundelde geluidsbestanden naar www/nida_dua/sounds/ (eenmalig)."""
    src_dir = os.path.join(component_dir, "sounds")
    if not os.path.isdir(src_dir):
        return

    dest_dir = hass.config.path("www", "nida_dua", "sounds")
    os.makedirs(dest_dir, exist_ok=True)

    for filename in os.listdir(src_dir):
        if not filename.endswith(".mp3"):
            continue
        src = os.path.join(src_dir, filename)
        dest = os.path.join(dest_dir, filename)
        if not os.path.exists(dest):
            shutil.copy2(src, dest)
            _LOGGER.info("Nida Dua: geluid gekopieerd: %s", filename)
