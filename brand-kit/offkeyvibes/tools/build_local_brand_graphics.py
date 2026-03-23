from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
KIT = ROOT / "brand-kit" / "offkeyvibes"
OUT = KIT / "generated" / "social"
OFFKEY_SQUARE = ROOT / "logos" / "offkeyvibes" / "square"
OKV_SQUARE = ROOT / "logos" / "okv" / "square"

ASSETS = {
    "banner": ROOT / "banners" / "wide" / "offkeyvibes-banner-wide-final.png",
    "logo_horizontal": ROOT / "logos" / "offkeyvibes" / "offkeyvibes-logo-horizontal-transparent-final.png",
    "logo_square": ROOT / "logos" / "offkeyvibes" / "square" / "offkeyvibes-logo-square-break-the-chains-final.png",
    "okv_mark": ROOT / "logos" / "okv" / "offkeyvibes-okv-logo-transparent-final.png",
    "btc_cover": ROOT / "songs" / "break-the-chains" / "break-the-chains-cover.png",
    "btc_banner": ROOT / "songs" / "break-the-chains" / "break-the-chains-banner-cover.png",
    "wall_offkeyvibes": ROOT / "wallpapers" / "desktop" / "offkeyvibes-desktop-wall.png",
    "wall_okv": ROOT / "wallpapers" / "desktop" / "okv-desktop-wall.png",
    "wall_okv_rocks": ROOT / "wallpapers" / "desktop" / "okv-dot-rocks-desktop-wall.png",
}

COLORS = {
    "obsidian": "#030102",
    "charred_black": "#0A0103",
    "smoke_brown": "#1C0E0D",
    "burnt_rust": "#4D1E11",
    "cinder_red": "#8A2516",
    "ember_orange": "#C05829",
    "signal_orange": "#E56F1D",
    "molten_gold": "#DC9747",
    "ash_gold": "#D8C786",
    "bone_white": "#F4F8F3",
    "deep_violet_shadow": "#2E003C",
}

IMPACT = r"C:\Windows\Fonts\impact.ttf"
ARIAL_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
BAHN = r"C:\Windows\Fonts\bahnschrift.ttf"


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def crop_alpha(image: Image.Image) -> Image.Image:
    if "A" not in image.getbands():
        return image
    bbox = image.getchannel("A").getbbox()
    return image.crop(bbox) if bbox else image


def make_background(path: Path, size: tuple[int, int], centering=(0.5, 0.5), blur=2.0) -> Image.Image:
    base = Image.open(path).convert("RGB")
    base = ImageOps.fit(base, size, method=Image.Resampling.LANCZOS, centering=centering)
    base = ImageEnhance.Color(base).enhance(0.86)
    base = ImageEnhance.Contrast(base).enhance(1.18)
    if blur:
        base = base.filter(ImageFilter.GaussianBlur(blur))
    canvas = base.convert("RGBA")
    canvas = Image.alpha_composite(canvas, Image.new("RGBA", size, rgba(COLORS["obsidian"], 118)))

    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    w, h = size
    glow_draw.ellipse((-w * 0.18, -h * 0.08, w * 0.55, h * 0.72), fill=rgba(COLORS["signal_orange"], 70))
    glow_draw.ellipse((w * 0.46, h * 0.58, w * 1.12, h * 1.24), fill=rgba(COLORS["cinder_red"], 72))
    glow_draw.ellipse((w * 0.55, -h * 0.18, w * 1.08, h * 0.32), fill=rgba(COLORS["molten_gold"], 24))
    glow = glow.filter(ImageFilter.GaussianBlur(max(50, int(min(size) * 0.08))))
    return Image.alpha_composite(canvas, glow)


def make_clean_wallpaper_background(path: Path, size: tuple[int, int], centering=(0.5, 0.5)) -> Image.Image:
    base = Image.open(path).convert("RGB")
    base = ImageOps.fit(base, size, method=Image.Resampling.LANCZOS, centering=centering)
    base = ImageEnhance.Color(base).enhance(0.96)
    base = ImageEnhance.Contrast(base).enhance(1.08)
    canvas = base.convert("RGBA")
    canvas = Image.alpha_composite(canvas, Image.new("RGBA", size, rgba(COLORS["obsidian"], 48)))
    return canvas


def add_frame(canvas: Image.Image, margin: int = 34, radius: int = 84) -> None:
    w, h = canvas.size
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (margin, margin, w - margin, h - margin),
        radius=radius,
        outline=rgba(COLORS["ember_orange"], 112),
        width=3,
    )
    draw.rounded_rectangle(
        (margin + 18, margin + 18, w - margin - 18, h - margin - 18),
        radius=radius - 14,
        outline=rgba(COLORS["bone_white"], 16),
        width=2,
    )
    canvas.alpha_composite(layer)


def add_noise(canvas: Image.Image, amount: int = 11) -> None:
    noise = Image.effect_noise(canvas.size, amount).convert("L")
    noise = ImageEnhance.Contrast(noise).enhance(1.35)
    alpha = noise.point(lambda p: int(max(0, p - 118) * 0.18))
    grain = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    grain.putalpha(alpha)
    canvas.alpha_composite(grain)


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_x: int,
    top: int,
    text_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    spacing: int = 8,
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
):
    bbox = draw.multiline_textbbox((0, 0), text, font=text_font, spacing=spacing, align="center", stroke_width=stroke_width)
    width = bbox[2] - bbox[0]
    x = center_x - width / 2
    draw.multiline_text(
        (x, top),
        text,
        font=text_font,
        fill=fill,
        spacing=spacing,
        align="center",
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def paste_logo(canvas: Image.Image, path: Path, box: tuple[int, int], center_x: int, top: int) -> None:
    logo = crop_alpha(Image.open(path).convert("RGBA"))
    logo = ImageOps.contain(logo, box, method=Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", logo.size, rgba(COLORS["deep_violet_shadow"], 0))
    shadow.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.33)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    glow = Image.new("RGBA", logo.size, rgba(COLORS["signal_orange"], 0))
    glow.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.15)))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    left = int(center_x - logo.size[0] / 2)
    canvas.alpha_composite(glow, (left, top - 4))
    canvas.alpha_composite(shadow, (left, top + 12))
    canvas.alpha_composite(logo, (left, top))


def add_plate(canvas: Image.Image, box: tuple[int, int, int, int], radius: int = 68) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(box, radius=radius, fill=rgba(COLORS["charred_black"], 164), outline=rgba(COLORS["bone_white"], 28), width=2)
    draw.rounded_rectangle(
        (box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10),
        radius=radius - 8,
        outline=rgba(COLORS["signal_orange"], 46),
        width=2,
    )
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    canvas.alpha_composite(layer)


def build_square_logo_plate(background_path: Path, logo_path: Path, output_path: Path, logo_box: tuple[int, int], centering=(0.5, 0.5)) -> Path:
    size = (1600, 1600)
    canvas = make_background(background_path, size, centering=centering, blur=1.6)
    add_frame(canvas, margin=42, radius=116)
    add_plate(canvas, (146, 448, 1454, 1152), radius=104)
    paste_logo(canvas, logo_path, logo_box, 800, 558)
    add_noise(canvas)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, optimize=True)
    return output_path


def build_okv_rocks_square() -> Path:
    size = (1080, 1080)
    canvas = make_clean_wallpaper_background(ASSETS["wall_okv_rocks"], size, centering=(0.5, 0.5))
    add_frame(canvas, margin=28, radius=92)

    draw = ImageDraw.Draw(canvas)
    small = font(BAHN, 30)
    big = font(IMPACT, 154)
    sub = font(ARIAL_BOLD, 42)
    meta = font(BAHN, 28)

    draw_centered_text(draw, "REMEMBER THE EASY ONE", 540, 126, small, rgba(COLORS["ash_gold"], 214), spacing=4)
    draw_centered_text(
        draw,
        "okv.rocks",
        540,
        650,
        big,
        rgba(COLORS["bone_white"], 255),
        spacing=0,
        stroke_width=4,
        stroke_fill=rgba(COLORS["deep_violet_shadow"], 240),
    )
    draw_centered_text(draw, "links  /  updates  /  contact", 540, 858, sub, rgba(COLORS["molten_gold"], 255), spacing=4)
    draw_centered_text(draw, "OffKeyVibes", 540, 944, meta, rgba(COLORS["bone_white"], 180), spacing=4)

    add_noise(canvas)
    path = OUT / "okv-rocks-core-memory-square.png"
    canvas.save(path, optimize=True)
    return path


def build_okv_rocks_story() -> Path:
    size = (1080, 1920)
    canvas = make_clean_wallpaper_background(ASSETS["wall_okv_rocks"], size, centering=(0.5, 0.5))
    add_frame(canvas, margin=30, radius=110)

    draw = ImageDraw.Draw(canvas)
    kicker = font(BAHN, 38)
    big = font(IMPACT, 182)
    sub = font(ARIAL_BOLD, 60)
    small = font(BAHN, 34)

    draw_centered_text(draw, "KEEP THIS ONE IN YOUR HEAD", 540, 188, kicker, rgba(COLORS["ash_gold"], 220), spacing=4)
    draw_centered_text(
        draw,
        "okv.rocks",
        540,
        1014,
        big,
        rgba(COLORS["bone_white"], 255),
        spacing=0,
        stroke_width=5,
        stroke_fill=rgba(COLORS["deep_violet_shadow"], 240),
    )
    draw_centered_text(draw, "everything starts here", 540, 1268, sub, rgba(COLORS["molten_gold"], 255), spacing=6)
    draw_centered_text(draw, "OffKeyVibes  |  Cassatt, South Carolina", 540, 1756, small, rgba(COLORS["bone_white"], 175), spacing=4)

    add_noise(canvas)
    path = OUT / "okv-rocks-core-memory-story.png"
    canvas.save(path, optimize=True)
    return path


def build_okv_mark_square() -> Path:
    size = (1080, 1080)
    canvas = make_clean_wallpaper_background(ASSETS["wall_okv"], size, centering=(0.5, 0.5))
    add_frame(canvas, margin=28, radius=92)
    draw = ImageDraw.Draw(canvas)
    kicker = font(BAHN, 32)
    body = font(ARIAL_BOLD, 44)
    meta = font(BAHN, 28)

    draw_centered_text(draw, "REMEMBER OKV", 540, 136, kicker, rgba(COLORS["ash_gold"], 220), spacing=4)
    draw_centered_text(draw, "short for OffKeyVibes", 540, 860, body, rgba(COLORS["molten_gold"], 255), spacing=4)
    draw_centered_text(draw, "OffKeyVibes", 540, 932, meta, rgba(COLORS["bone_white"], 182), spacing=4)

    add_noise(canvas)
    path = OUT / "okv-short-mark-square.png"
    canvas.save(path, optimize=True)
    return path


def build_offkeyvibes_identity_square() -> Path:
    size = (1080, 1080)
    canvas = make_clean_wallpaper_background(ASSETS["wall_offkeyvibes"], size, centering=(0.5, 0.5))
    add_frame(canvas, margin=28, radius=92)
    draw = ImageDraw.Draw(canvas)
    line = font(ARIAL_BOLD, 54)
    body = font(BAHN, 30)
    domain = font(IMPACT, 116)

    draw_centered_text(draw, "OUT OF CASSATT, SOUTH CAROLINA", 540, 118, line, rgba(COLORS["bone_white"], 255), spacing=6)
    draw_centered_text(draw, "Heavy original music built from pressure, rage, release, and survival.", 540, 822, body, rgba(COLORS["ash_gold"], 228), spacing=8)
    draw_centered_text(draw, "okv.rocks", 540, 900, domain, rgba(COLORS["molten_gold"], 255), spacing=0, stroke_width=3, stroke_fill=rgba(COLORS["deep_violet_shadow"], 220))

    add_noise(canvas)
    path = OUT / "offkeyvibes-core-identity-square.png"
    canvas.save(path, optimize=True)
    return path


def build_break_the_chains_status() -> Path:
    size = (1080, 1080)
    canvas = make_background(ASSETS["btc_cover"], size, centering=(0.50, 0.50), blur=2.0)
    add_frame(canvas, margin=28, radius=92)

    cover_strip = Image.open(ASSETS["btc_banner"]).convert("RGB")
    cover_strip = ImageOps.fit(cover_strip, (840, 286), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")
    cover_strip = ImageEnhance.Color(cover_strip).enhance(0.92)
    add_plate(canvas, (120, 126, 960, 436), radius=74)
    canvas.alpha_composite(cover_strip, (120, 126))
    canvas.alpha_composite(Image.new("RGBA", (840, 286), rgba(COLORS["obsidian"], 68)), (120, 126))

    draw = ImageDraw.Draw(canvas)
    title = font(IMPACT, 120)
    label = font(ARIAL_BOLD, 46)
    body = font(BAHN, 34)

    draw_centered_text(draw, "BREAK THE CHAINS", 540, 500, title, rgba(COLORS["bone_white"], 255), stroke_width=4, stroke_fill=rgba(COLORS["deep_violet_shadow"], 230))
    draw_centered_text(draw, "LYRICS LIVE NOW", 540, 688, label, rgba(COLORS["molten_gold"], 255), spacing=6)
    draw_centered_text(draw, "Track release still in progress.", 540, 760, body, rgba(COLORS["bone_white"], 210), spacing=6)
    draw_centered_text(draw, "Follow the build at okv.rocks", 540, 908, label, rgba(COLORS["signal_orange"], 255), spacing=6)

    add_noise(canvas)
    path = OUT / "break-the-chains-status-square.png"
    canvas.save(path, optimize=True)
    return path


def build_contact_sheet(paths: list[Path]) -> Path:
    thumbs = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        thumbs.append(ImageOps.fit(image, (520, 520), method=Image.Resampling.LANCZOS))

    sheet = Image.new("RGB", (1120, 1120), rgba(COLORS["obsidian"])[:3])
    positions = [(30, 30), (570, 30), (30, 570), (570, 570)]
    for image, pos in zip(thumbs, positions):
        sheet.paste(image, pos)

    draw = ImageDraw.Draw(sheet)
    label_font = font(BAHN, 26)
    labels = [
        "OffKeyVibes core",
        "OKV short mark",
        "okv.rocks square",
        "okv.rocks story",
    ]
    for pos, label in zip(positions, labels):
        draw.rounded_rectangle((pos[0] + 14, pos[1] + 442, pos[0] + 350, pos[1] + 494), radius=18, fill=rgba(COLORS["charred_black"], 200))
        draw.text((pos[0] + 34, pos[1] + 453), label, fill=rgba(COLORS["bone_white"])[:3], font=label_font)

    path = OUT / "contact-sheet.png"
    sheet.save(path, optimize=True)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    OFFKEY_SQUARE.mkdir(parents=True, exist_ok=True)
    OKV_SQUARE.mkdir(parents=True, exist_ok=True)
    core_logo_outputs = [
        build_square_logo_plate(
            ASSETS["wall_offkeyvibes"],
            ASSETS["logo_horizontal"],
            OFFKEY_SQUARE / "offkeyvibes-logo-square-core-final.png",
            (1160, 430),
            centering=(0.5, 0.5),
        ),
        build_square_logo_plate(
            ASSETS["wall_okv"],
            ASSETS["okv_mark"],
            OKV_SQUARE / "offkeyvibes-okv-logo-square-core-final.png",
            (980, 980),
            centering=(0.5, 0.5),
        ),
    ]
    outputs = [
        build_offkeyvibes_identity_square(),
        build_okv_mark_square(),
        build_okv_rocks_square(),
        build_okv_rocks_story(),
        build_break_the_chains_status(),
    ]
    outputs.append(build_contact_sheet(outputs[:4]))
    for path in core_logo_outputs + outputs:
        print(path)


if __name__ == "__main__":
    main()
