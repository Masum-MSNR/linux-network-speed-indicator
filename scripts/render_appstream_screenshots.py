#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1280
HEIGHT = 720
TOP_BAR_HEIGHT = 42
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / 'assets' / 'screenshots'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')


def font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_SMALL = font('DejaVuSans.ttf', 20)
FONT_BODY = font('DejaVuSans.ttf', 24)
FONT_LABEL = font('DejaVuSans.ttf', 22)
FONT_CHECK = font('DejaVuSans.ttf', 24)
FONT_CLOCK = font('DejaVuSans-Bold.ttf', 22)
FONT_CHEVRON = font('DejaVuSans.ttf', 20)


def make_background() -> Image.Image:
    image = Image.new('RGBA', (WIDTH, HEIGHT), '#16181e')
    draw = ImageDraw.Draw(image)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        red = int(19 + (40 - 19) * ratio)
        green = int(22 + (31 - 22) * ratio)
        blue = int(30 + (46 - 30) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(red, green, blue, 255))

    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse((-120, 160, 420, 700), fill=(247, 165, 88, 48))
    overlay_draw.ellipse((740, -80, 1320, 520), fill=(88, 151, 247, 58))
    overlay_draw.ellipse((420, 180, 980, 760), fill=(112, 83, 212, 34))
    overlay = overlay.filter(ImageFilter.GaussianBlur(54))
    image = Image.alpha_composite(image, overlay)

    wallpaper = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    wallpaper_draw = ImageDraw.Draw(wallpaper)
    wallpaper_draw.polygon([(70, 720), (360, 150), (540, 720)], fill=(226, 110, 78, 186))
    wallpaper_draw.polygon([(280, 720), (560, 210), (830, 720)], fill=(217, 92, 70, 142))
    wallpaper_draw.polygon([(560, 720), (860, 250), (1130, 720)], fill=(99, 87, 187, 150))
    wallpaper_draw.polygon([(840, 720), (1090, 210), (1280, 720)], fill=(70, 135, 221, 165))
    wallpaper = wallpaper.filter(ImageFilter.GaussianBlur(2))
    image = Image.alpha_composite(image, wallpaper)

    return image


def draw_top_bar(base: Image.Image, label: str) -> None:
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, 0, WIDTH, TOP_BAR_HEIGHT), fill=(19, 20, 24, 225))
    draw.text((22, 9), 'Activities', font=FONT_SMALL, fill=(238, 238, 242, 255))
    draw.text((WIDTH // 2 - 58, 9), 'Thu 29 Apr  17:42', font=FONT_CLOCK, fill=(244, 245, 248, 255))

    pill_x = WIDTH - 330
    pill_y = 5
    pill_w = 262
    pill_h = 31
    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        radius=14,
        fill=(44, 47, 57, 230),
    )
    draw.text((pill_x + 16, pill_y + 5), label, font=FONT_SMALL, fill=(244, 247, 252, 255))

    dot_x = WIDTH - 36
    dot_y = 15
    draw.ellipse((dot_x, dot_y, dot_x + 10, dot_y + 10), fill=(110, 220, 140, 255))


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 24) -> None:
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(bounds, radius=radius, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base.alpha_composite(shadow)


def add_focus_glow(base: Image.Image, bounds: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    glow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(bounds, radius=18, fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    base.alpha_composite(glow)


def build_overview() -> Image.Image:
    image = make_background()
    draw_top_bar(image, '↓ 5.09 KB/s   ↑ 4.06 KB/s')

    add_focus_glow(image, (944, 4, 1220, 38), (98, 167, 255, 54))

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((52, 560, 498, 666), radius=18, fill=(18, 20, 26, 156))
    draw.text((82, 588), 'Live speed in the top bar', font=FONT_BODY, fill=(242, 245, 250, 255))
    draw.text((82, 625), 'Download and upload rates stay visible while you work.', font=FONT_SMALL, fill=(220, 224, 232, 255))
    return image.convert('RGB')


def build_menu() -> Image.Image:
    image = make_background()
    draw_top_bar(image, '↓ 46.3 KB/s   ↑ 3.29 KB/s')
    add_focus_glow(image, (944, 4, 1220, 38), (98, 167, 255, 44))
    add_shadow(image, (900, 72, 1170, 438), radius=22)

    draw = ImageDraw.Draw(image)
    panel = (908, 80, 1162, 430)
    draw.rounded_rectangle(panel, radius=22, fill=(60, 63, 74, 248))

    rows = [
        ('Units', True, False),
        ('Display', True, False),
        ('Refresh Rate', True, False),
        ('Start on Login', False, True),
        ('Quit Speed Meter', False, False),
    ]

    y = 126
    for index, (label, has_chevron, checked) in enumerate(rows):
        if index == 4:
            draw.line((936, y - 16, 1134, y - 16), fill=(122, 126, 139, 148), width=1)
            y += 14

        if checked:
            draw.text((934, y - 3), '✓', font=FONT_CHECK, fill=(244, 246, 249, 255))
            text_x = 966
        else:
            text_x = 938

        draw.text((text_x, y), label, font=FONT_LABEL, fill=(248, 248, 251, 255))

        if has_chevron:
            draw.text((1128, y + 3), '›', font=FONT_CHEVRON, fill=(221, 224, 231, 255))

        y += 64

    return image.convert('RGB')


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_overview().save(OUTPUT_DIR / 'overview.png', optimize=True)
    build_menu().save(OUTPUT_DIR / 'menu.png', optimize=True)


if __name__ == '__main__':
    main()