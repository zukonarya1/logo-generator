#!/usr/bin/env python3
"""
generate_logo.py — Generate a logo PNG using the Gemini image generation API.

Usage:
    python generate_logo.py "your prompt here"
    python generate_logo.py               # reads from prompts/default.txt
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "output"
PROMPTS_DIR = Path(__file__).parent / "prompts"
MODEL = "gemini-3-pro-image-preview"


def get_prompt() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    default_prompt_file = PROMPTS_DIR / "default.txt"
    if default_prompt_file.exists():
        return default_prompt_file.read_text().strip()
    print("Error: no prompt provided and prompts/default.txt not found.")
    print("Usage: python generate_logo.py \"your prompt here\"")
    sys.exit(1)


def generate(prompt: str) -> Path:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print(f"Generating with {MODEL}...")
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="1:1",
                image_size="1K",
            ),
        ),
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = OUTPUT_DIR / f"{timestamp}.png"

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            return output_path

    print("Error: no image returned in response.")
    sys.exit(1)


if __name__ == "__main__":
    prompt = get_prompt()
    output_path = generate(prompt)
    print(f"Saved: {output_path}")
