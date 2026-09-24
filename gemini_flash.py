from typing import List
from google import genai
from pydantic import BaseModel, Field

from .config import settings
from .models import PanelOutline

class OutlineResponse(BaseModel):
    panels: List[PanelOutline] = Field(min_length=5, max_length=5)

_client = None

def _get_client():
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client

def generate_outline(user_prompt: str) -> list[dict]:
    """Generate a strict five-panel outline for the comic."""
    if settings.mock_mode:
        return [
            {
                "panel": i,
                "title": title,
                "scene_description": desc,
                "image_prompt": image,
            }
            for i, (title, desc, image) in enumerate([
                ("The Forest Edge", "The hero arrives at the edge of a mysterious forest.", "comic book illustration, brave fox at a forest edge, cinematic lighting"),
                ("Into the Deep Woods", "The hero follows a glowing trail beneath tall trees.", "comic book illustration, fox walking through enchanted woods, glowing trail"),
                ("The Hidden Clearing", "A magical clearing reveals a surprising guardian.", "comic book illustration, enchanted clearing, friendly magical guardian"),
                ("A Brave Choice", "The hero chooses courage and helps restore the forest.", "comic book illustration, fox helping a magical forest guardian, heroic moment"),
                ("Homeward", "The hero returns home carrying a new story to tell.", "comic book illustration, fox leaving enchanted forest at sunset, warm ending"),
            ], start=1)
        ]

    prompt = f"""
You are a professional comic-book planner.

Create exactly 5 sequential panels for this story idea:
{user_prompt}

For every panel provide:
- panel: integer 1 through 5
- title: short title
- scene_description: 1-2 sentence visual scene description
- image_prompt: a detailed prompt for a text-to-image model

Keep the same main characters visually coherent across panels. Do not put speech text or captions inside the image prompt.
"""
    client = _get_client()
    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": OutlineResponse.model_json_schema(),
        },
    )
    parsed = OutlineResponse.model_validate_json(response.text)
    return [panel.model_dump() for panel in parsed.panels]
