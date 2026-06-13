"""Nida Dua — media player helpers."""
from __future__ import annotations

import logging
import socket

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    CONF_EVENING_ENABLED,
    CONF_EVENING_END,
    CONF_EVENING_START,
    CONF_EVENING_VOLUME,
    CONF_VOLUME,
    DEFAULT_EVENING_END,
    DEFAULT_EVENING_START,
    DEFAULT_EVENING_VOLUME,
    DEFAULT_VOLUME,
)

_LOGGER = logging.getLogger(__name__)

_SOUND_BASE = "/local/nida_dua/sounds"


def get_sound_url(hass: HomeAssistant, filename: str) -> str:
    """Bouw de volledige lokale URL voor een geluidsbestand."""
    base = hass.config.internal_url or hass.config.external_url
    if not base:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = "127.0.0.1"
        base = f"http://{ip}:8123"
    return f"{base.rstrip('/')}{_SOUND_BASE}/{filename}"


def get_current_volume(opts: dict) -> float:
    """Geef het juiste volume terug op basis van tijd (dag of avond)."""
    day_vol = float(opts.get(CONF_VOLUME, DEFAULT_VOLUME)) / 100

    if not opts.get(CONF_EVENING_ENABLED, False):
        return day_vol

    hour = dt_util.now().hour
    start = int(opts.get(CONF_EVENING_START, DEFAULT_EVENING_START))
    end = int(opts.get(CONF_EVENING_END, DEFAULT_EVENING_END))

    # Avond kan over middernacht lopen (bijv. 21:00–07:00)
    if start > end:
        in_evening = hour >= start or hour < end
    else:
        in_evening = start <= hour < end

    if in_evening:
        return float(opts.get(CONF_EVENING_VOLUME, DEFAULT_EVENING_VOLUME)) / 100
    return day_vol


async def async_play_dua(
    hass: HomeAssistant,
    speakers: list[str],
    sound_url: str,
    volume: float,
) -> None:
    """Speel een dua af op de opgegeven mediaspelers."""
    for entity_id in speakers:
        try:
            await hass.services.async_call(
                "media_player",
                "volume_set",
                {"entity_id": entity_id, "volume_level": volume},
                blocking=False,
            )
            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": entity_id,
                    "media_content_id": sound_url,
                    "media_content_type": "music",
                },
                blocking=False,
            )
        except Exception:
            _LOGGER.exception("Kon dua niet afspelen op %s", entity_id)
