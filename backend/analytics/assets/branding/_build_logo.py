"""Build clean DuraCapital branding PNGs for PDF export."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
NAVY = (15, 55, 90)
CYAN = (64, 180, 210)
WHITE = (255, 255, 255)


def _font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_logo(path: Path, width: int = 900, height: int = 220) -> None:
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Icon: rounded rectangle with crescent split
    icon_box = (20, 35, 150, 175)
    draw.rounded_rectangle(icon_box, radius=28, fill=NAVY)
    # Cyan crescent on the right of the icon
    draw.ellipse((70, 30, 190, 180), fill=CYAN)
    draw.ellipse((95, 30, 215, 180), fill=(255, 255, 255, 0))
    # Re-draw navy left half over transparent hole for clean crescent
    draw.pieslice(icon_box, 90, 270, fill=NAVY)
    draw.ellipse((78, 42, 168, 168), fill=CYAN)
    draw.ellipse((98, 42, 188, 168), fill=NAVY)

    title_font = _font(72, bold=True)
    tag_font = _font(28, bold=False)
    draw.text((180, 48), "Dura", font=title_font, fill=NAVY)
    dura_w = draw.textlength("Dura", font=title_font)
    draw.text((180 + dura_w, 48), "Capital", font=title_font, fill=CYAN)

    tag = "mathematics matters"
    tag_x = 180 + dura_w + 8
    tag_y = 135
    draw.line((tag_x, tag_y - 8, tag_x + draw.textlength(tag, font=tag_font), tag_y - 8), fill=CYAN, width=2)
    draw.text((tag_x, tag_y), tag, font=tag_font, fill=CYAN)

    img.save(path)


def refine_header_logo() -> None:
    """Prefer the extracted header crop when usable; otherwise generate."""
    crop = ROOT / "duracapital_logo_header_crop.png"
    out = ROOT / "duracapital_logo.png"
    if crop.exists():
        img = Image.open(crop).convert("RGBA")
        # Trim mostly-white margins
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        # Ensure white background for PDF embedding
        bg = Image.new("RGB", img.size, WHITE)
        bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        bg.save(out)
    else:
        build_logo(out)


if __name__ == "__main__":
    build_logo(ROOT / "duracapital_logo_generated.png")
    refine_header_logo()
    # Also keep a generated fallback
    if not (ROOT / "duracapital_logo.png").exists():
        build_logo(ROOT / "duracapital_logo.png")
    print("logo ready", (ROOT / "duracapital_logo.png").exists())
