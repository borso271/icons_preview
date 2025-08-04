#!/usr/bin/env python3
"""
make_icon.py  –  Generate an Apple-style 3-D icon with OpenAI Images.

Usage:
    python make_icon.py "billiard table"
"""

import argparse
import base64
import os
from datetime import datetime
from openai import OpenAI

MODEL_NAME = "gpt-image-1"          # <— change if you’re on a different image model
OUT_DIR    = "output"               # folder where PNGs will be written
# --------------------------------

# Style recipe split into named cues (edit to taste)
STYLE_CUES = {
    "perspective": "isometric 3/4 view",
    "lighting": "soft global illumination with gentle shadows",
    "materials": "slightly matte plastic surfaces",
    "style": "modern Apple-emoji aesthetic",
    "background": "clean white studio backdrop",
    "palette": "bright but tasteful colors",
    "detail_level": "minimal yet highly readable"
}


def build_prompt(subject: str) -> str:
    """Turn the STYLE_CUES + subject into a single text prompt."""
    cues_text = ", ".join(STYLE_CUES.values())
    return f"A single, center-framed 3-D icon of a {subject}. {cues_text}."


def generate_icon(subject: str, client: OpenAI) -> bytes:
    """Call the OpenAI Images API and return raw PNG bytes."""
    prompt = build_prompt(subject)
    result = client.images.generate(
        model=MODEL_NAME,
        prompt=prompt,
        n=1,
        size="1024x1024",
        
    )
    # Decode the base64 result
    return base64.b64decode(result.data[0].b64_json)


def save_image(png_bytes: bytes, subject: str) -> str:
    """Write PNG to disk, return the file path."""
    os.makedirs(OUT_DIR, exist_ok=True)
    safe_name = subject.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{safe_name}_{timestamp}.png"
    path = os.path.join(OUT_DIR, filename)
    with open(path, "wb") as f:
        f.write(png_bytes)
    return path


def main():
    parser = argparse.ArgumentParser(description="Generate a 3-D emoji-style icon.")
    parser.add_argument("subject", help="e.g. 'fire hydrant', 'Petra monument'")
    args = parser.parse_args()

    client = OpenAI()                   # Assumes OPENAI_API_KEY is set
    png_bytes = generate_icon(args.subject, client)
    out_path = save_image(png_bytes, args.subject)
    print(f"✅ Icon saved to {out_path}")


if __name__ == "__main__":
    main()
