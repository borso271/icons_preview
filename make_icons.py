#!/usr/bin/env python3
"""
make_icons_from_json.py  –  Generate Apple-style 3-D icons for every object
                            listed in a JSON array.

JSON input format (array of objects):
[
  {
    "name": "Laptop",
    "category": "office",
    "fun_fact": "...",               # unused here but fine to keep
    "short_description": "...",      # unused
    "rarity": "common"               # unused
  },
  ...
]

Usage
-----
# From a JSON file:
python make_icons.py output.json

# From stdin:
cat objects.json | python make_icons.py -
"""

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime
from typing import List, Dict

from openai import OpenAI

# ── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_NAME = "gpt-image-1"          # change if you use a different image model
OUT_DIR    = "output"               # images will be written here


STYLE_CUES = {
    "perspective": "isometric 3/4 view",
    "lighting": "soft global illumination with gentle shadows",
    "materials": "slightly matte plastic surfaces",
    "style": "modern Apple-emoji aesthetic",
    "background": "clean white studio backdrop",
    "palette": "bright but tasteful colors",
    "detail_level": "minimal yet highly readable",
}
# ──────────────────────────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """Lower-case, replace non-alphanumerics with underscores."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def build_prompt(subject: str) -> str:
    cues_text = ", ".join(STYLE_CUES.values())
    return f"A single, center-framed 3-D icon of a {subject}. {cues_text}."


def generate_icon(subject: str, client: OpenAI) -> bytes:
    prompt = build_prompt(subject)
    result = client.images.generate(
        model=MODEL_NAME,
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    return base64.b64decode(result.data[0].b64_json)


def save_image(png_bytes: bytes, name: str, category: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    filename = f"{slugify(name)}_{slugify(category)}.png"
    path = os.path.join(OUT_DIR, filename)

    # If a file with that name already exists, append a timestamp
    if os.path.exists(path):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(OUT_DIR, f"{slugify(name)}_{slugify(category)}_{ts}.png")

    with open(path, "wb") as f:
        f.write(png_bytes)
    return path


def load_json(source: str) -> List[Dict]:
    """Load JSON from a file path or stdin ('-')."""
    if source == "-":
        data = json.load(sys.stdin)
    else:
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON must be an array of objects.")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate icons from a JSON array.")
    parser.add_argument(
        "json_source",
        help="Path to JSON file, or '-' to read from stdin.",
    )
    args = parser.parse_args()

    objects = load_json(args.json_source)
    client = OpenAI()  # requires OPENAI_API_KEY env variable

    for obj in objects:
        try:
            name     = obj["name"]
            category = obj["category"]
        except KeyError:
            print(f"⚠️  Skipping entry (missing 'name' or 'category'): {obj}", file=sys.stderr)
            continue

        print(f"➜ Generating icon for {name} ({category}) …", end="", flush=True)
        png_bytes = generate_icon(name, client)
        path      = save_image(png_bytes, name, category)
        print(f" saved → {path}")


if __name__ == "__main__":
    main()
