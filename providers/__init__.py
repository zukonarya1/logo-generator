import sys

VALID_PROVIDERS = ["gemini", "fal", "openai"]


def resolve_provider(name: str):
    if name not in VALID_PROVIDERS:
        print(f"Error: unknown provider '{name}'. Valid: {', '.join(VALID_PROVIDERS)}")
        sys.exit(1)
    if name == "gemini":
        from .gemini import generate
    elif name == "fal":
        from .fal import generate
    elif name == "openai":
        from .openai_provider import generate
    return generate
