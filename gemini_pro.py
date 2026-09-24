from typing import List
from google import genai
from pydantic import BaseModel, Field

from .config import settings
from .models import PanelStory

class StoryResponse(BaseModel):
    panels: List[PanelStory] = Field(min_length=5, max_length=5)

_client = None

def _get_client():
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client

def generate_story(outline: list[dict]) -> list[dict]:
    """Expand the five-panel outline into narration, captions and dialogue."""
    if settings.mock_mode:
        return [
            {
                "panel": item["panel"],
                "title": item["title"],
                "scene_description": item["scene_description"],
                "narration": f"The adventure continues through panel {item['panel']}.",
                "caption": "The forest whispers in the distance.",
                "dialogue": "We can do this!",
            }
            for item in outline
        ]

    outline_text = "\n".join(
        f"{p['panel']}. {p['title']} — {p['scene_description']}"
        for p in outline
    )
    prompt = f"""
You are an experienced comic-book writer.

Expand this five-panel outline into a cohesive comic story.

OUTLINE:
{outline_text}

For each panel return:
- panel
- title
- scene_description
- narration: concise prose describing action/emotion
- caption: brief ambient caption or sound description
- dialogue: character dialogue, if useful

Keep the story coherent across all five panels. Avoid markdown and do not add extra panels.
"""
    client = _get_client()
    response = client.models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": StoryResponse.model_json_schema(),
        },
    )
    parsed = StoryResponse.model_validate_json(response.text)
    return [panel.model_dump() for panel in parsed.panels]
