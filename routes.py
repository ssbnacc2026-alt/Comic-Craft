import traceback
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .models import PromptRequest

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def _full_prompt(prompt: str, character_name: str, setting: str, tone: str, style: str) -> str:
    return (
        f"Story prompt: {prompt}\n"
        f"Main character: {character_name}\n"
        f"Setting: {setting}\n"
        f"Tone: {tone}\n"
        f"Art style: {style}"
    )

def _generate_pipeline(data: PromptRequest):
    outline = generate_outline(
        _full_prompt(data.prompt, data.character_name, data.setting, data.tone, data.style)
    )
    if len(outline) != 5:
        raise ValueError("The outline model must return exactly 5 panels.")

    stories = generate_story(outline)
    if len(stories) != 5:
        raise ValueError("The story model must return exactly 5 panels.")

    images = [
        generate_image(
            f"{panel['image_prompt']}, consistent character design, {data.style}"
        )
        for panel in outline
    ]
    layout = build_comic_layout(images, stories, outline)
    pdf_path = save_pdf(layout)
    return layout, pdf_path

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...),
):
    try:
        data = PromptRequest(
            prompt=prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            style=style,
        )
        layout, pdf_path = _generate_pipeline(data)
        web_pdf_path = "/" + pdf_path.replace("\\", "/")
        return templates.TemplateResponse(
            "comic_preview.html",
            {"request": request, "layout": layout, "pdf_path": web_pdf_path},
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/generate-comic/json")
async def generate_comic_json(data: PromptRequest):
    try:
        layout, pdf_path = _generate_pipeline(data)
        return {
            "layout": layout,
            "pdf_path": "/" + pdf_path.replace("\\", "/"),
        }
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/download-pdf")
async def download_pdf(pdf_path: str):
    path = Path(pdf_path)
    if not path.exists() or path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=path.name,
    )

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str):
    return templates.TemplateResponse(
        "export_success.html",
        {"request": request, "pdf_path": pdf_path},
    )

@router.get("/test-image")
async def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, comic book art"):
    try:
        image_path = generate_image(prompt)
        return {"message": "Image generated successfully", "path": image_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
