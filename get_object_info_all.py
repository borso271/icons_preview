#!/usr/bin/env python3
"""
get_object_info.py – Generate kid-friendly metadata for objects.

Run ONE item:
    python get_object_info.py "laptop"

Run the default list (edit OBJECT_LIST below):
    python get_object_info_all.py
"""

# OBJECT_LIST =['Laptop', 'Pen']

OBJECT_LIST =['Laptop', 'Pen', 'Notebook', 'Keyboard', 'Stapler', 'Highlighter', 'Paper Clip', 'Desk Chair', 'Printer', 'Coffee Mug', 'Pencil', 'Backpack', 'Book', 'Crayon', 'Glue Stick', 'Ruler', 'Lunchbox', 'Eraser', 'Whiteboard', 'Classroom Globe', 'Daisy', 'Rock', 'Leaf', 'Stick', 'Watering Can', 'Butterfly', 'Snail', 'Ladybug', 'Birdhouse', 'Garden Gnome', 'Swing', 'Slide', 'Ball', 'Sandbox', 'Seesaw', 'Hula Hoop', 'Frisbee', 'Bubbles', 'Climbing Frame', 'Bouncer', 'Dog', 'Cat', 'Bird', 'Fly', 'Fish', 'Rabbit', 'Frog', 'Ladybug', 'Duck', 'Squirrel', 'Car', 'Bus', 'Bicycle', 'Scooter', 'Train', 'Fire Truck', 'Tractor', 'Ice Cream Truck', 'Plane', 'Boat', 'Toothbrush', 'Towel', 'Lamp', 'Chair', 'Cushion', 'Remote Control', 'Fan', 'Clock', 'Painting', 'Plant Pot', 'T-Shirt', 'Socks', 'Shoes', 'Hat', 'Jacket', 'Scarf', 'Gloves', 'Sunglasses', 'Crown', 'Umbrella', 'Sofa', 'TV', 'Lamp', 'Remote', 'Rug', 'Bookshelf', 'Console', 'Blanket', 'Candle', 'Record Player', 'Teddy Bear', 'Toy Car', 'Crayon', 'LEGO', 'Paintbrush', 'Doll', 'Puzzle Piece', 'Stickers', 'Magic Wand', 'Paint Brush']




#!/usr/bin/env python3
"""
get_object_info.py – Generate kid-friendly metadata for a list of objects.
"""

import argparse
import json
from enum import Enum
from typing import List, Optional

from openai import OpenAI
from pydantic import BaseModel

# ── Enumerations ──────────────────────────────────────────────────────────────
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


# ── Schema for structured output ──────────────────────────────────────────────
class ObjectInfo(BaseModel):
    fun_fact: str
    short_description: str
    rarity: Rarity
    category: Category


# ── Prompt builder ────────────────────────────────────────────────────────────
def build_messages(name: str, hint: Optional[str] = None) -> List[dict]:
    system_msg = {
        "role": "system",
        "content": (
            "Return JSON that conforms to the ObjectInfo schema.\n"
            "- fun_fact: ≤ 15 words, educational, written in Blippi's playful voice "
            "(e.g. \"Pens use ink to write—some click, some twist, and some even sparkle!\").\n"
            "- short_description: 1–2 simple sentences suitable for 6-year-olds.\n"
            "- rarity: pick one of {common, rare, super rare}.\n"
            "- category: pick one of "
            "{animals, clothing, garden, house, living room, office, playground,"
            "school, toys & crafts, transportation}."
        ),
    }

    user_msg = {"role": "user", "content": f"Object name: {name}"}
    if hint:
        user_msg["content"] += f"\nHint: {hint}"

    return [system_msg, user_msg]


# ── Fetch a single object’s info ──────────────────────────────────────────────
def fetch_object_info(client: OpenAI, obj_name: str, hint: Optional[str] = None) -> ObjectInfo:
    response = client.responses.parse(
        model="gpt-4o",
        input=build_messages(obj_name, hint),
        text_format=ObjectInfo,
    )
    return response.output_parsed




# ── Main script ───────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Get structured, kid-friendly info for objects."
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="Single object name (e.g. 'laptop'). If omitted, uses the built-in list.",
    )
    parser.add_argument(
        "--hint",
        default=None,
        help="Optional disambiguation hint for the single-name mode.",
    )
    args = parser.parse_args()

    # OpenAI client (relies on OPENAI_API_KEY env variable)
    client = OpenAI()   

    # Determine object list
    if args.name:
        objects = [args.name]
        hints   = [args.hint]
    else:
        objects = OBJECT_LIST
        hints   = [None] * len(objects)

    # Collect results
    results = []
    for obj, h in zip(objects, hints):
        info = fetch_object_info(client, obj, h)
        entry = info.model_dump()
        entry["name"] = obj            # ← include the object name
        results.append(entry)

    # Output JSON array
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()