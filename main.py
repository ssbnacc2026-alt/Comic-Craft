from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI comic story creator using Gemini models and Stable Diffusion.",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "mock_mode": settings.mock_mode,
        "image_provider": settings.image_provider,
        "gemini_flash_model": settings.gemini_flash_model,
        "gemini_pro_model": settings.gemini_pro_model,
    }
