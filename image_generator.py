from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont

from .config import settings

_pipe = None

def sanitize_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return (value[:80] or "panel").lower()

def _get_pipe():
    global _pipe
    if _pipe is not None:
        return _pipe

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        token = settings.hf_api_key or None
        dtype = torch.float16 if settings.sd_device in {"cuda", "auto"} and torch.cuda.is_available() else torch.float32
        _pipe = StableDiffusionPipeline.from_pretrained(
            settings.sd_model_id,
            torch_dtype=dtype,
            token=token,
        )

        if settings.sd_device == "cuda" or (settings.sd_device == "auto" and torch.cuda.is_available()):
            _pipe = _pipe.to("cuda")
        elif settings.sd_device == "mps" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            _pipe = _pipe.to("mps")
        else:
            _pipe = _pipe.to("cpu")
        return _pipe
    except Exception:
        if settings.allow_mock_fallback:
            return None
        raise

def _mock_image(prompt: str, path: Path):
    image = Image.new("RGB", (settings.sd_width, settings.sd_height), (224, 236, 248))
    draw = ImageDraw.Draw(image)
    title = "ComicCraft Preview"
    body = prompt[:180]
    font = ImageFont.load_default()
    draw.rectangle((18, 18, image.width - 18, image.height - 18), outline=(30, 60, 90), width=4)
    draw.text((35, 40), title, fill=(20, 40, 60), font=font)
    draw.text((35, 90), "Image provider: mock", fill=(20, 40, 60), font=font)
    draw.multiline_text((35, 140), body, fill=(20, 40, 60), font=font, spacing=8)
    image.save(path)

def generate_image(prompt: str, filename: str | None = None) -> str:
    filename = filename or sanitize_filename(prompt)
    path = settings.panels_dir / f"{filename}.png"

    if settings.mock_mode:
        _mock_image(prompt, path)
        return str(path.relative_to(Path.cwd())).replace("\\", "/")

    pipe = _get_pipe()
    if pipe is None:
        _mock_image(prompt, path)
        return str(path.relative_to(Path.cwd())).replace("\\", "/")

    image = pipe(
        prompt,
        num_inference_steps=settings.sd_steps,
        guidance_scale=settings.sd_guidance_scale,
        width=settings.sd_width,
        height=settings.sd_height,
    ).images[0]
    image.save(path)
    return str(path.relative_to(Path.cwd())).replace("\\", "/")
