from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    environment: str = "development"
    debug: bool = True

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-3.8-flash"
    gemini_pro_model: str = "gemini-3.1-pro-preview"

    hf_api_key: str = ""
    image_provider: str = "diffusers"  # diffusers | mock
    sd_model_id: str = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    sd_device: str = "auto"
    sd_steps: int = 25
    sd_guidance_scale: float = 7.5
    sd_width: int = 512
    sd_height: int = 512

    mock_mode: bool = False
    allow_mock_fallback: bool = True

    panels_dir: Path = BASE_DIR / "static" / "panels"
    exports_dir: Path = BASE_DIR / "static" / "exports"
    fonts_dir: Path = BASE_DIR / "static" / "fonts"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

for directory in (settings.panels_dir, settings.exports_dir, settings.fonts_dir):
    directory.mkdir(parents=True, exist_ok=True)
