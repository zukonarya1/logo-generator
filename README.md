# Logo Generator

A Python script that generates logo images using the Google Gemini image generation API.

## Requirements

- Python 3.11+
- A [Gemini API key](https://aistudio.google.com/apikey)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

## Usage

Pass a prompt as a CLI argument:

```bash
python generate_logo.py "A minimal vector hourglass logo mark, purple to pink gradient"
```

Or write your prompt to `prompts/default.txt` and run without arguments:

```bash
python generate_logo.py
```

Output is saved to `output/YYYY-MM-DD_HH-MM-SS.png`.

## Notes

- Model: `gemini-3-pro-image-preview`
- Output: 1024×1024px PNG (1:1 aspect ratio)
- Each run creates a new timestamped file — previous outputs are never overwritten
- The `output/` directory is gitignored
