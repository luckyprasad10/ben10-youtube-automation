import os
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

from src.config import TEMP_DIR, CHANNEL_HANDLE

def get_font(size: int):
    """Loads a bold punchy font across Windows and Linux cloud runners."""
    font_candidates = [
        "Impact", "impact.ttf",
        "Arial Black", "ariblk.ttf",
        "Segoe UI Bold", "segoeuib.ttf",
        "DejaVuSans-Bold.ttf",
        "LiberationSans-Bold.ttf",
        "Arial", "arial.ttf"
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    pos: tuple,
    text: str,
    font: ImageFont.ImageFont,
    fill_color: tuple = (255, 255, 255),
    outline_color: tuple = (0, 0, 0),
    outline_width: int = 4
):
    """Draws punchy text with thick dark outline for maximum readability."""
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=fill_color)

def generate_high_ctr_thumbnail(
    keyframe_path: Path,
    output_path: Optional[Path] = None,
    series: str = "Ben 10",
    season: int = 1,
    episode: int = 1,
    hook_text: str = "EPIC BATTLE!"
) -> Optional[Path]:
    """
    Creates an eye-catching 1280x720 thumbnail:
    - 16:9 resize + contrast boost
    - Ben 10 Neon-Green Glowing Outer Border
    - Episode Badge (e.g. 'S01 • EP 01')
    - Punchy Hook Text overlay
    - Channel Brand Badge
    """
    if output_path is None:
        output_path = TEMP_DIR / f"thumb_{series.replace(' ', '_')}_s{season}e{episode}.jpg"

    try:
        # 1. Load and resize to 1280x720
        im = Image.open(keyframe_path).convert("RGB")
        im = im.resize((1280, 720), Image.Resampling.LANCZOS)

        # 2. Boost color vibrancy & contrast for cartoon look
        color_enhancer = ImageEnhance.Color(im)
        im = color_enhancer.enhance(1.25)
        contrast_enhancer = ImageEnhance.Contrast(im)
        im = contrast_enhancer.enhance(1.15)

        draw = ImageDraw.Draw(im)

        # 3. Add Ben 10 Signature Neon-Green Border Glow
        border_color = (57, 255, 20)  # Neon Green
        border_width = 8
        for i in range(border_width):
            draw.rectangle([i, i, 1280 - 1 - i, 720 - 1 - i], outline=border_color)

        # 4. Top-Left Series & Episode Badge
        badge_font = get_font(38)
        badge_text = f" {series.upper()} • S{season:02d} EP{episode:02d} "
        badge_box = draw.textbbox((30, 30), badge_text, font=badge_font)
        # Background pill with neon border
        draw.rectangle([badge_box[0] - 8, badge_box[1] - 6, badge_box[2] + 8, badge_box[3] + 6], fill=(10, 10, 10), outline=border_color, width=3)
        draw_text_with_outline(draw, (30, 30), badge_text, badge_font, fill_color=(57, 255, 20), outline_color=(0, 0, 0), outline_width=2)

        # 5. Bottom Big Hook Text (Curiosity Driver)
        hook_font = get_font(64)
        clean_hook = hook_text.upper().strip()
        if len(clean_hook) > 28:
            clean_hook = clean_hook[:25] + "..."
            
        hook_bbox = draw.textbbox((0, 0), clean_hook, font=hook_font)
        hook_w = hook_bbox[2] - hook_bbox[0]
        hook_x = (1280 - hook_w) // 2
        hook_y = 580

        # Background banner for bottom text
        banner_top = hook_y - 12
        banner_bot = hook_y + (hook_bbox[3] - hook_bbox[1]) + 16
        banner_overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        banner_draw = ImageDraw.Draw(banner_overlay)
        banner_draw.rectangle([0, banner_top, 1280, banner_bot], fill=(0, 0, 0, 200))
        im = Image.alpha_composite(im.convert("RGBA"), banner_overlay).convert("RGB")
        draw = ImageDraw.Draw(im)

        draw_text_with_outline(
            draw,
            (hook_x, hook_y),
            clean_hook,
            hook_font,
            fill_color=(255, 230, 0),  # Electric Yellow
            outline_color=(0, 0, 0),
            outline_width=6
        )

        # 6. Channel Watermark in Top Right
        brand_font = get_font(26)
        brand_text = f" {CHANNEL_HANDLE} "
        b_box = draw.textbbox((0, 0), brand_text, font=brand_font)
        bw = b_box[2] - b_box[0]
        bx = 1250 - bw
        draw.rectangle([bx - 6, 26, 1250, 64], fill=(0, 0, 0, 180), outline=(57, 255, 20), width=2)
        draw_text_with_outline(draw, (bx, 30), brand_text, brand_font, fill_color=(255, 255, 255), outline_color=(0, 0, 0), outline_width=2)

        # 7. Save output
        im.save(output_path, "JPEG", quality=95)
        print(f"[Thumbnail] Generated high-CTR thumbnail: {output_path.name}")
        return output_path

    except Exception as e:
        print(f"[Thumbnail] Failed to generate thumbnail: {e}")
        return None

