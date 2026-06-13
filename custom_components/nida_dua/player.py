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


def _lan_ip() -> str:
    """Geef het echte LAN-IP van de HA-server terug via socket-trick."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""


def get_sound_url(hass: HomeAssistant, filename: str) -> str:
    """Bouw de volledige lokale URL voor een geluidsbestand.

    internal_url / external_url kan '0.0.0.0' bevatten (luisteradres van HA),
    wat Sonos niet kan bereiken. Gebruik dan het echte LAN-IP via socket.
    """
    port = hass.config.api.port if hass.config.api else 8123
    use_ssl = hass.config.api.use_ssl if hass.config.api else False
    scheme = "https" if use_ssl else "http"

    for candidate in [hass.config.internal_url, hass.config.external_url]:
        if candidate and "0.0.0.0" not in candidate:
            return f"{candidate.rstrip('/')}{_SOUND_BASE}/{filename}"

    ip = _lan_ip()
    base = f"{scheme}://{ip}:{port}" if ip else f"{scheme}://homeassistant.local:{port}"
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
