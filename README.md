# Nida Dua

Home Assistant custom component om islamitische duas (gebedssmeekbedes) af te spelen via je mediaspelers.

## Installatie

1. Kopieer de map `custom_components/nida_dua` naar `/config/custom_components/`
2. Herstart Home Assistant
3. Ga naar **Instellingen → Integraties → Integratie toevoegen → Nida Dua**
4. Voer je mediaspeler entity_id en gewenst volume in

## Geluidsbestanden

Kopieer je MP3-bestanden naar:
```
/config/www/nida_dua/sounds/
```

Bestandsnamen komen overeen met de `sound`-sleutel in `const.py`:

| Dua                  | Bestandsnaam            |
|----------------------|------------------------|
| Slaap dua            | `dua_sleep.mp3`        |
| Binnenkomen huis dua | `dua_enter_home.mp3`   |

## Entiteiten

| Entiteit                        | Type   | Omschrijving                                        |
|---------------------------------|--------|-----------------------------------------------------|
| `button.dua_sleep`                   | Button | Druk om de slaap-dua direct af te spelen                              |
| `switch.dua_sleep_schakelaar`        | Switch | Zet aan om de slaap-dua af te spelen (gaat automatisch na 5s uit)    |
| `button.dua_enter_home`              | Button | Druk om de binnenkomen-dua direct af te spelen                        |
| `switch.dua_enter_home_schakelaar`   | Switch | Zet aan om de binnenkomen-dua af te spelen (gaat automatisch na 5s uit) |

## Gebruik in automatisering

### Via knop (dashboard)
Voeg `button.dua_sleep` toe aan je Lovelace dashboard.

### Via automatisering (bedtijdroutine)
```yaml
automation:
  - alias: "Bedtijdroutine — slaap dua"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.dua_sleep_schakelaar
```

### Via script
```yaml
script:
  speel_slaap_dua:
    sequence:
      - service: button.press
        target:
          entity_id: button.dua_sleep
```
