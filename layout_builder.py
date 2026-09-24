from pathlib import Path
from .models import ComicLayoutItem

def build_comic_layout(image_paths: list[str], stories: list[dict], outline: list[dict]) -> list[dict]:
    """Match each generated image to its corresponding story panel."""
    by_panel = {item["panel"]: item for item in stories}
    layout = []

    for index, (image_path, outline_item) in enumerate(zip(image_paths, outline), start=1):
        story = by_panel.get(outline_item["panel"], {})
        narration = story.get("narration", "")
        caption = story.get("caption", "")
        dialogue = story.get("dialogue", "")
        text_parts = [p for p in (caption, narration, dialogue) if p]

        layout.append(
            ComicLayoutItem(
                panel=index,
                title=outline_item.get("title", f"Panel {index}"),
                image_path=image_path,
                text="\n\n".join(text_parts),
                scene_description=outline_item.get("scene_description", ""),
                narration=narration,
                caption=caption,
                dialogue=dialogue,
            ).model_dump()
        )

    return layout
