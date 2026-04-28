#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / 'assets' / 'screenshots'
REFERENCE_DIR = OUTPUT_DIR / 'reference'
MENU_SOURCE_PATH = REFERENCE_DIR / 'menu-source.png'
INDICATOR_SOURCE_PATH = REFERENCE_DIR / 'indicator-source.png'

RESAMPLING = getattr(Image, 'Resampling', Image)
LANCZOS = RESAMPLING.LANCZOS
OVERVIEW_SCALE = 6.0
MENU_SCALE = 2.5


def load_reference(path: Path) -> Image.Image:
    return Image.open(path).convert('RGBA')


def scale_image(source: Image.Image, scale: float) -> Image.Image:
    return source.resize(
        (max(1, int(round(source.width * scale))), max(1, int(round(source.height * scale)))),
        LANCZOS,
    )


def build_overview() -> Image.Image:
    indicator_source = load_reference(INDICATOR_SOURCE_PATH)
    return scale_image(indicator_source, OVERVIEW_SCALE).convert('RGB')


def build_menu() -> Image.Image:
    menu_source = load_reference(MENU_SOURCE_PATH)
    return scale_image(menu_source, MENU_SCALE).convert('RGB')


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_overview().save(OUTPUT_DIR / 'overview.png', optimize=True)
    build_menu().save(OUTPUT_DIR / 'menu.png', optimize=True)


if __name__ == '__main__':
    main()