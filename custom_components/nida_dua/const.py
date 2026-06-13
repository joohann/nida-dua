"""Nida Dua — constants."""

DOMAIN = "nida_dua"

CONF_SPEAKER = "speaker"
CONF_VOLUME = "volume"
CONF_EVENING_ENABLED = "evening_enabled"
CONF_EVENING_VOLUME = "evening_volume"
CONF_EVENING_START = "evening_start_hour"
CONF_EVENING_END = "evening_end_hour"

DUA_SLEEP = "sleep"
DUA_ENTER_HOME = "enter_home"

DUAS: dict[str, dict] = {
    DUA_SLEEP: {
        "name": "Slaap dua",
        "name_en": "Sleep dua",
        "arabic": "اللَّهُمَّ بِاسْمِكَ أَمُوتُ وَأَحْيَا",
        "transliteration": "Allahumma bismika amutu wa ahya",
        "sound": "dua_sleep.mp3",
    },
    DUA_ENTER_HOME: {
        "name": "Binnenkomen huis dua",
        "name_en": "Enter home dua",
        "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ خَيْرَ الْمَوْلَجِ وَخَيْرَ الْمَخْرَجِ",
        "transliteration": "Allahumma inni as'aluka khayral mawlaji wa khayral makhraji",
        "sound": "dua_enter_home.mp3",
    },
}

DEFAULT_VOLUME = 40          # percent
DEFAULT_EVENING_VOLUME = 20  # percent
DEFAULT_EVENING_START = 21   # hour
DEFAULT_EVENING_END = 7      # hour
DEFAULT_SPEAKER: list[str] = []


def conf_dua_enabled(dua_key: str) -> str:
    return f"enabled_{dua_key}"
