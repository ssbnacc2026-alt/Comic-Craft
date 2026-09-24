from app.layout_builder import build_comic_layout

def test_build_comic_layout():
    outline = [
        {"panel": 1, "title": "One", "scene_description": "Scene one", "image_prompt": "image one"},
        {"panel": 2, "title": "Two", "scene_description": "Scene two", "image_prompt": "image two"},
    ]
    stories = [
        {"panel": 1, "title": "One", "scene_description": "Scene one", "narration": "N1", "caption": "C1", "dialogue": "D1"},
        {"panel": 2, "title": "Two", "scene_description": "Scene two", "narration": "N2", "caption": "C2", "dialogue": ""},
    ]
    layout = build_comic_layout(["static/panels/a.png", "static/panels/b.png"], stories, outline)
    assert len(layout) == 2
    assert layout[0]["title"] == "One"
    assert "N1" in layout[0]["text"]
