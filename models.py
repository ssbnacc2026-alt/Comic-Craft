from pydantic import BaseModel, Field, field_validator

class PromptRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    character_name: str = Field(min_length=1, max_length=100)
    setting: str = Field(min_length=1, max_length=200)
    tone: str = Field(min_length=1, max_length=100)
    style: str = Field(min_length=1, max_length=100)

    @field_validator("*")
    @classmethod
    def strip_values(cls, value: str) -> str:
        return value.strip()

class PanelOutline(BaseModel):
    panel: int
    title: str
    scene_description: str
    image_prompt: str

class PanelStory(BaseModel):
    panel: int
    title: str
    scene_description: str
    narration: str
    caption: str
    dialogue: str = ""

class ComicLayoutItem(BaseModel):
    panel: int
    title: str
    image_path: str
    text: str
    scene_description: str
    narration: str = ""
    caption: str = ""
    dialogue: str = ""
