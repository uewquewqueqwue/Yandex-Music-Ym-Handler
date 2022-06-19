import os
import sys

from PIL import Image, ImageEnhance, ImageStat

PIXEL_MAP = ((0x01, 0x08), (0x02, 0x10), (0x04, 0x20), (0x40, 0x80))

BRAILLE_DOTS_HEIGHT = 4
BRAILLE_DOTS_WIDTH = 2

BRAILLE_UNICODE_START = 0x2800


def _floor_to_nearest_multiple(number: int, multiple: int):
    return (number // multiple) * multiple


def _resize_portrait(image: Image, width: int):
    wpercent = width / float(image.size[0])
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((width, hsize), Image.Resampling.LANCZOS)
    return image


def generate_art(
    source_path: str | os.PathLike,
    threshold: int = None,
    art_width: int = 100,
    contrast: float = None,
) -> str:
    """Generates braille art from a picture."""
    symbols = []
    image = Image.open(source_path)
    image = _resize_portrait(image, art_width)

    image = image.convert("L")
    if contrast is not None:
        image = ImageEnhance.Contrast(image).enhance(contrast)

    if threshold is None:
        threshold = ImageStat.Stat(image).mean[0]

    for height in range(
        0,
        _floor_to_nearest_multiple(image.height, BRAILLE_DOTS_HEIGHT),
        BRAILLE_DOTS_HEIGHT,
    ):
        for width in range(
            0,
            _floor_to_nearest_multiple(image.width, BRAILLE_DOTS_WIDTH),
            BRAILLE_DOTS_WIDTH,
        ):
            symbol_relative_pos = 0
            for part_height in range(BRAILLE_DOTS_HEIGHT):
                for part_width in range(BRAILLE_DOTS_WIDTH):
                    if (
                        image.getpixel((width + part_width, height + part_height))
                        > threshold
                    ):
                        symbol_relative_pos += PIXEL_MAP[part_height][part_width]
            symbols.append(chr(BRAILLE_UNICODE_START + symbol_relative_pos))

    art_string = ""
    count = 0
    for _ in range(image.height // BRAILLE_DOTS_HEIGHT):
        for _ in range(image.width // BRAILLE_DOTS_WIDTH):
            art_string += symbols[count]
            count += 1
        art_string += "\n"

    return art_string


sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
