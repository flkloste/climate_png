#!/usr/bin/env python3
"""Render the Home Assistant "Climate" card as a PNG (runs as a local HA add-on).

  1. POST the Jinja template (climate.j2) to the HA REST API (/api/template), so HA fills in live sensor values.
  2. Extract the SVG from the returned markdown data URI.
  3. Convert the SVG to PNG with rsvg-convert and write it to OUT_DIR (default /config/www/climate.png).

Inside the add-on, the Supervisor proxy and SUPERVISOR_TOKEN are used automatically.
Outside HA, set HA_URL and HA_TOKEN (long-lived token) and OUT_DIR.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HA_URL = (os.environ.get("HA_URL") or "http://supervisor/core").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN") or os.environ["SUPERVISOR_TOKEN"]
OUT_DIR = os.path.abspath(os.environ.get("OUT_DIR", "/config/www"))
WIDTH = int(os.environ.get("WIDTH", "1440"))  # pixel width of the PNG (the card is 360 units wide)
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "climate.j2")
INTERVAL = int(os.environ.get("INTERVAL", "300"))
try:  # add-on options (Settings > Add-ons > Climate PNG > Configuration)
    with open("/data/options.json", encoding="utf-8") as f:
        _opts = json.load(f)
    INTERVAL = int(_opts.get("interval", INTERVAL))
    WIDTH = int(_opts.get("width", WIDTH))
except (OSError, ValueError):
    pass


def render_once() -> None:
    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()
    req = urllib.request.Request(
        HA_URL + "/api/template",
        data=json.dumps({"template": template}).encode("utf-8"),
        headers={"Authorization": "Bearer " + HA_TOKEN, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        rendered = resp.read().decode("utf-8")
    m = re.search(r"data:image/svg\+xml;utf8,([^)]*)\)", rendered)
    if not m:
        raise RuntimeError("no SVG data URI in the template output: " + rendered[:200])
    os.makedirs(OUT_DIR, exist_ok=True)
    svg_path = os.path.join(OUT_DIR, "climate.svg")
    tmp_png = os.path.join(OUT_DIR, "climate.tmp.png")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(urllib.parse.unquote(m.group(1)))
    subprocess.run(["rsvg-convert", "-w", str(WIDTH), "-o", tmp_png, svg_path], check=True)
    shutil.move(tmp_png, os.path.join(OUT_DIR, "climate.png"))  # atomic replace


if __name__ == "__main__":
    once = "--once" in sys.argv
    while True:
        try:
            render_once()
            print(time.strftime("%H:%M:%S"), "rendered", flush=True)
        except Exception as exc:  # keep the last good PNG and try again next round
            print(time.strftime("%H:%M:%S"), "error:", exc, file=sys.stderr, flush=True)
            if once:
                sys.exit(1)
        if once:
            break
        time.sleep(INTERVAL)