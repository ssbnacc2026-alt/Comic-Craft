from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from .config import settings

def _font_path() -> str | None:
    candidates = [
        settings.fonts_dir / "DejaVuSans.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return None

def save_pdf(layout: list[dict]) -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = _font_path()
    unicode_font = False
    if font_path:
        pdf.add_font("ComicFont", "", font_path)
        unicode_font = True

    for panel in layout:
        pdf.add_page()
        if unicode_font:
            pdf.set_font("ComicFont", "", 16)
        else:
            pdf.set_font("Helvetica", "", 16)

        pdf.cell(0, 12, f"Panel {panel['panel']}: {panel['title']}", new_x="LMARGIN", new_y="NEXT", align="C")

        image_path = panel["image_path"]
        if Path(image_path).exists():
            pdf.image(image_path, x=10, y=35, w=190, h=100, keep_aspect_ratio=True)
        else:
            pdf.set_xy(10, 35)
            pdf.multi_cell(190, 8, f"Image missing: {image_path}")

        pdf.set_y(145)
        if unicode_font:
            pdf.set_font("ComicFont", "", 11)
        else:
            pdf.set_font("Helvetica", "", 11)

        text = "\n\n".join(
            x for x in [
                panel.get("scene_description", ""),
                panel.get("caption", ""),
                panel.get("narration", ""),
                panel.get("dialogue", ""),
            ] if x
        )
        if not unicode_font:
            text = text.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(190, 7, text)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = settings.exports_dir / f"comic_{timestamp}.pdf"
    pdf.output(str(output))
    return str(output)
