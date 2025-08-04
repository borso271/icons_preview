#!/usr/bin/env python3

from __future__ import annotations
"""
get_object_info.py — Query OpenAI for structured information about an object.

The script returns:
  • fun_fact          – playful trivia (≤ 15 words)
  • short_description – 1–2 sentence what-it-is blurb
  • rarity            – one of: common · rare · super rare
  • category          – one of: animals · toys · food · tools · nature · people · places · vehicles · other

Prerequisites:
  pip install openai pydantic
  export OPENAI_API_KEY="sk-..."
"""


import argparse
from enum import Enum
import json
from pydantic import BaseModel
from openai import OpenAI


object_list =['Laptop', 'Pen', 'Notebook', 'Keyboard', 'Stapler', 'Highlighter', 'Paper Clip', 'Desk Chair', 'Printer', 'Coffee Mug', 'Pencil', 'Backpack', 'Book', 'Crayon', 'Glue Stick', 'Ruler', 'Lunchbox', 'Eraser', 'Whiteboard', 'Classroom Globe', 'Daisy', 'Rock', 'Leaf', 'Stick', 'Watering Can', 'Butterfly', 'Snail', 'Ladybug', 'Birdhouse', 'Garden Gnome', 'Swing', 'Slide', 'Ball', 'Sandbox', 'Seesaw', 'Hula Hoop', 'Frisbee', 'Bubbles', 'Climbing Frame', 'Bouncer', 'Dog', 'Cat', 'Bird', 'Fly', 'Fish', 'Rabbit', 'Frog', 'Ladybug', 'Duck', 'Squirrel', 'Car', 'Bus', 'Bicycle', 'Scooter', 'Train', 'Fire Truck', 'Tractor', 'Ice Cream Truck', 'Plane', 'Boat', 'Toothbrush', 'Towel', 'Lamp', 'Chair', 'Cushion', 'Remote Control', 'Fan', 'Clock', 'Painting', 'Plant Pot', 'T-Shirt', 'Socks', 'Shoes', 'Hat', 'Jacket', 'Scarf', 'Gloves', 'Sunglasses', 'Crown', 'Umbrella', 'Sofa', 'TV', 'Lamp', 'Remote', 'Rug', 'Bookshelf', 'Console', 'Blanket', 'Candle', 'Record Player', 'Teddy Bear', 'Toy Car', 'Crayon', 'LEGO', 'Paintbrush', 'Doll', 'Puzzle Piece', 'Stickers', 'Magic Wand', 'Paint Brush']

# ── Enumerations ───────────────────────────────────────────────────────────────
class Rarity(str, Enum):
    common = "common"
    rare = "rare"
    super_rare = "super rare"


class Category(str, Enum):
    animals        = "animals"
    clothing       = "clothing"
    garden         = "garden"
    house          = "house"
    living_room    = "living room"
    office         = "office"
    playground     = "playground"
    school         = "school"
    toys_crafts    = "toys & crafts"
    transportation = "transportation"


# ── Schema used for structured-output parsing ─────────────────────────────────
class ObjectInfo(BaseModel):
    fun_fact: str
    short_description: str
    rarity: Rarity
    category: Category


def build_messages(name: str, hint: str | None) -> list[dict]:
    """
    Craft the chat messages for structured-output parsing.

    • fun_fact  – ≤ 15 words, educational, written in Blippi’s playful voice
    • short_description – 1-2 kid-friendly sentences a 6-year-old can grasp
    • rarity  – common | rare | super rare
    • category – animals | clothing | garden | house | living room | office | playground | school | toys & crafts | transportation
    
    """

    system_msg = {
        "role": "system",
        "content": (
            "Return JSON that conforms to the ObjectInfo schema.\n"
            "- fun_fact: ≤ 15 words, educational, written in Blippi's upbeat style (\"Wow, kids! …\").\n"
            "- short_description: 1–2 concise sentences suitable for children.\n"
            "- rarity: choose exactly one of {common, rare, super rare}.\n"
            "- category: choose exactly one of {animals, toys, food, tools, nature, people, places, vehicles, other}."
        ),
    }

    user_msg = {"role": "user", "content": f"Object name: {name}"}
    if hint:
        user_msg["content"] += f"\nHint: {hint}"

    return [system_msg, user_msg]


# ── Main script ───────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Get structured info about an object.")
    parser.add_argument("name", help="Object name, e.g. 'fire hydrant'")
    parser.add_argument("--hint", default=None, help="Optional disambiguation hint")
    args = parser.parse_args()

    client = OpenAI()                               # needs OPENAI_API_KEY env var

    response = client.responses.parse(                # ⇐ structured-output call
        model="gpt-4o",
        input=build_messages(args.name, args.hint),
        text_format=ObjectInfo,
    )

    info: ObjectInfo = response.output_parsed

    # Pydantic v2: use model_dump_json() instead of json()
    print(info.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
