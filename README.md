# Home Assistant add-ons

## Climate PNG

Renders the "Climate" house card (humidity / temperature per room) as `/config/www/climate.png`
every few minutes, so it can be shown as a camera (e.g. in the Android app camera widget).

Setup: see the camera snippet below.

```yaml
# configuration.yaml
camera:
  - platform: local_file
    name: Climate house
    file_path: /config/www/climate.png
```
