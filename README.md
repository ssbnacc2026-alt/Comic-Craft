# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application based on the supplied project documentation. It keeps the documented pipeline:

1. User enters story prompt, character, setting, tone, and art style.
2. Gemini Flash creates a structured five-panel outline.
3. Gemini Pro expands the outline into narration, captions, and dialogue.
4. Stable Diffusion via Hugging Face Diffusers creates one illustration per panel.
5. A layout builder joins text and images.
6. FPDF2 exports the finished comic as a multi-page PDF.
7. Jinja2 renders the homepage, preview page, and export flow.

## Important current-API update

The source document specifies the older `google-generativeai` SDK and Gemini 1.5 Flash/Pro model IDs. Current Google documentation recommends the `google-genai` SDK, and the current model catalog lists newer Gemini 3.x models. This implementation therefore uses `google-genai` with `gemini-3.8-flash` for the outline and `gemini-3.1-pro-preview` for the detailed story while retaining the source architecture and Flash/Pro roles.

The image pipeline remains Diffusers/Stable Diffusion as described by the project documentation.

## 1. Prerequisites

- Python 3.10+ recommended
- A Gemini API key for real story generation
- A machine capable of running Stable Diffusion locally (GPU recommended)
- Hugging Face access if the selected model requires authentication

## 2. Install

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure secrets

Copy `.env.example` to `.env`.

Set:

```dotenv
GEMINI_API_KEY=your_key
HF_API_KEY=your_huggingface_token
MOCK_MODE=false
```

Do not commit `.env`.

For a quick UI/API smoke test without AI credentials, set:

```dotenv
MOCK_MODE=true
```

Mock mode still runs the FastAPI → layout → PDF pipeline, but uses deterministic sample story data and placeholder images.

## 4. Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## 5. Test

Run:

```bash
python -m pytest -q
```

Then, with the server running, test image generation separately:

```text
GET /test-image?prompt=A%20fox%20in%20an%20enchanted%20forest
```

Test the JSON API from `/docs` using:

```json
{
  "prompt": "A brave fox exploring an enchanted forest.",
  "character_name": "Finn",
  "setting": "forest",
  "tone": "dramatic",
  "style": "comic book"
}
```

## 6. Project structure

```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── models.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/styles.css
│   ├── panels/
│   ├── exports/
│   └── fonts/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Troubleshooting

### Gemini authentication error

Check `GEMINI_API_KEY`, restart Uvicorn, and verify that the selected model is available to your API project.

### Stable Diffusion is too slow or runs out of memory

Use a CUDA-capable GPU, reduce `SD_WIDTH`, `SD_HEIGHT`, and `SD_STEPS`, or temporarily use `MOCK_MODE=true` to validate the rest of the application.

### PDF font issues

Place a Unicode TTF such as `DejaVuSans.ttf` in `static/fonts/`. The exporter also checks common system font locations.

### Generated files

Panel PNGs are stored in `static/panels/` and PDFs in `static/exports/`.
