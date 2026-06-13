"""Nida Dua — media player helpers."""
from __future__ import annotations

import logging
import socket

from homeassistant.core import HomeAssistant

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
