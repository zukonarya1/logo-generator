#!/usr/bin/env python3
"""
generate_logo.py — Generate a logo PNG using the Gemini image generation API.

Usage:
    python generate_logo.py "your prompt here"
    python generate_logo.py --file /path/to/prompt.txt

When --file is used, outputs (PNG + model note) are saved alongside the prompt file.
When a string prompt is used, outputs are saved to code/output/.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "output"
MODEL = "gemini-3-pro-image-preview"


def get_prompt() -> tuple[str, Path | None]:
    args = sys.argv[1:]

    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 >= len(args):
            print("Error: --file requires a path argument.")
            sys.exit(1)
        prompt_file = Path(args[idx + 1])
        if not prompt_file.exists():
            print(f"Error: prompt file not found: {prompt_file}")
            sys.exit(1)
        return prompt_file.read_text().strip(), prompt_file

    if args:
        return " ".join(args), None

    print("Error: no prompt provided.")
    print('Usage: python generate_logo.py "your prompt here"')
    print("       python generate_logo.py --file /path/to/prompt.txt")
    sys.exit(1)


def generate(prompt: str, prompt_file: Path | None) -> Path:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print(f"Generating with {MODEL}...")
    start = time.time()
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
    elapsed = time.time() - start
    print(f"Response received in {elapsed:.1f}s")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if prompt_file is not None:
        output_dir = prompt_file.parent
        stem = prompt_file.stem
        image_path = output_dir / f"{stem}_{timestamp}.png"
        note_path = output_dir / f"{stem}_{timestamp}.txt"
    else:
        OUTPUT_DIR.mkdir(exist_ok=True)
        image_path = OUTPUT_DIR / f"{timestamp}.png"
        note_path = None

    for part in response.candidates[0].content.parts:
        if part.text:
            print(f"Model note: {part.text.strip()}")
            if note_path:
                note_path.write_text(part.text.strip())
        if part.inline_data is not None:
            part.as_image().save(image_path)

    if not image_path.exists():
        print("Error: no image returned in response.")
        sys.exit(1)

    return image_path


if __name__ == "__main__":
    prompt, prompt_file = get_prompt()
    image_path = generate(prompt, prompt_file)
    print(f"Saved: {image_path}")
