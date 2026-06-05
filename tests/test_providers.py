import io
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call


# ── Gemini ──────────────────────────────────────────────────────────────────

def _make_gemini_response(image_bytes: bytes, text: str = "") -> MagicMock:
    """Build a mock Gemini API response containing one image part."""
    image_part = MagicMock()
    image_part.text = None
    image_part.inline_data = MagicMock()
    pil_image = MagicMock()
    def save_to_buf(buf, format):
        buf.write(image_bytes)
    pil_image.save.side_effect = save_to_buf
    image_part.as_image.return_value = pil_image

    text_part = MagicMock()
    text_part.text = text
    text_part.inline_data = None

    response = MagicMock()
    response.candidates[0].content.parts = [text_part, image_part] if text else [image_part]
    return response


@patch("providers.gemini.genai.Client")
def test_gemini_text_only_passes_string_contents(mock_client_cls, tmp_path):
    mock_client = mock_client_cls.return_value
    mock_client.models.generate_content.return_value = _make_gemini_response(b"PNG_BYTES")

    from providers.gemini import generate
    result = generate("A logo prompt", [])

    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["contents"] == "A logo prompt"
    assert isinstance(result, bytes)


@patch("providers.gemini.genai.Client")
def test_gemini_with_images_passes_list_contents(mock_client_cls, tmp_path):
    mock_client = mock_client_cls.return_value
    mock_client.models.generate_content.return_value = _make_gemini_response(b"PNG_BYTES")

    img = tmp_path / "shot.png"
    img.write_bytes(b"fake_png")

    from providers.gemini import generate
    result = generate("A composition prompt", [img])

    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    contents = call_kwargs["contents"]
    assert isinstance(contents, list)
    assert contents[-1] == "A composition prompt"
    assert len(contents) == 2  # 1 image part + text
    assert isinstance(result, bytes)


@patch("providers.gemini.genai.Client")
def test_gemini_raises_on_no_image_in_response(mock_client_cls):
    mock_client = mock_client_cls.return_value
    response = MagicMock()
    text_part = MagicMock()
    text_part.text = "some text"
    text_part.inline_data = None
    response.candidates[0].content.parts = [text_part]
    mock_client.models.generate_content.return_value = response

    from providers.gemini import generate
    with pytest.raises(RuntimeError, match="No image returned"):
        generate("prompt", [])
