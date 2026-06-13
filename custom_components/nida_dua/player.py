"""Nida Dua — media player helpers."""
from __future__ import annotations

import logging

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
    base = (hass.config.internal_url or hass.config.external_url or "").rstrip("/")
    if not base and hass.config.api:
        api = hass.config.api
        scheme = "https" if api.use_ssl else "http"
        base = f"{scheme}://{api.host}:{api.port}"
    if not base:
        base = "http://homeassistant.local:8123"
    return f"{base}{_SOUND_BASE}/{filename}"


def get_current_volume(opts: dict) -> float:
    """Geef het juiste volume terug op basis van tijd (dag of avond)."""
    day_vol = float(opts.get(CONF_VOLUME, DEFAULT_VOLUME)) / 100

    if not opts.get(CONF_EVENING_ENABLED, False):
        return day_vol

    hour = dt_util.now().hour
    start = int(opts.get(CONF_EVENING_START, DEFAULT_EVENING_START))
    end = int(opts.get(CONF_EVENING_END, DEFAULT_EVENING_END))

    if start > end:
        in_evening = hour >= start or hour < end
    else:
        in_evening = start <= hour < end

    return float(opts.get(CONF_EVENING_VOLUME, DEFAULT_EVENING_VOLUME)) / 100 if in_evening else day_vol


async def async_play_dua(
    hass: HomeAssistant,
    speakers: list[str] | str,
    sound_url: str,
    volume: float,
) -> None:
    """Speel een dua af op de opgegeven mediaspelers."""
    if isinstance(speakers, str):
        speakers = [s.strip() for s in speakers.split(",") if s.strip()]
    if not speakers:
        _LOGGER.warning("Nida Dua: geen mediaspeler geconfigureerd — stel deze in via Instellingen → Integraties → Nida Dua → Configureren")
        return

    _LOGGER.debug("Nida Dua: afspelen op %s — %s (vol %.0f%%)", speakers, sound_url, volume * 100)

    for entity_id in speakers:
        try:
            await hass.services.async_call(
                "media_player", "media_stop", {"entity_id": entity_id}, blocking=True,
            )
        except Exception:
            pass  # niet alle spelers ondersteunen stop; ga door

        try:
            await hass.services.async_call(
                "media_player",
                "volume_set",
                {"entity_id": entity_id, "volume_level": volume},
                blocking=True,
            )
            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": entity_id,
                    "media_content_id": sound_url,
                    "media_content_type": "music",
                },
                blocking=True,
            )
        except Exception:
            _LOGGER.exception("Nida Dua: kon dua niet afspelen op %s", entity_id)
