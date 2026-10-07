from pathlib import Path
from PIL import Image, ImageEnhance
import html


# ============================================================
# SETTINGS
# ============================================================

INPUT = Path("source-photo.png")
OUTPUT = Path("sonu-ascii.svg")

# Number of ASCII characters across
ASCII_WIDTH = 90

# Character proportions
CHAR_WIDTH = 7
CHAR_HEIGHT = 11

# Small margin around the actual portrait
CROP_MARGIN = 12

# Green terminal color
TEXT_COLOR = "#39d353"

# Dark pixels -> dense characters
# Bright pixels -> lighter characters
RAMP = "@%#*+=-:. "


# ============================================================
# CHECK INPUT
# ============================================================

if not INPUT.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT}"
    )

print(f"Reading {INPUT}...")


# ============================================================
# LOAD IMAGE
# ============================================================

image = Image.open(INPUT).convert("RGBA")

print(
    f"Original image: "
    f"{image.width} x {image.height}"
)


# ============================================================
# USE TRANSPARENCY TO FIND THE PORTRAIT
# ============================================================

alpha = image.getchannel("A")

# Find all pixels that are actually visible
bbox = alpha.getbbox()

if bbox is None:
    raise RuntimeError(
        "No visible subject was found in the image."
    )


# ============================================================
# CROP TO PORTRAIT
# ============================================================

left, top, right, bottom = bbox

left = max(0, left - CROP_MARGIN)
top = max(0, top - CROP_MARGIN)
right = min(image.width, right + CROP_MARGIN)
bottom = min(image.height, bottom + CROP_MARGIN)

image = image.crop(
    (left, top, right, bottom)
)

print(
    f"Cropped portrait: "
    f"{image.width} x {image.height}"
)


# ============================================================
# CONVERT TO GRAYSCALE
# ============================================================

rgb = image.convert("RGB")

gray = rgb.convert("L")


# ============================================================
# IMPROVE CONTRAST
# ============================================================

# This makes the beard, hair, eyes and facial contours
# stand out better in ASCII.

contrast = ImageEnhance.Contrast(gray)

gray = contrast.enhance(1.35)


# ============================================================
# RESIZE FOR ASCII
# ============================================================

aspect_ratio = gray.height / gray.width

ascii_height = max(
    1,
    int(
        ASCII_WIDTH
        * aspect_ratio
        * 0.50
    )
)

gray = gray.resize(
    (
        ASCII_WIDTH,
        ascii_height
    ),
    Image.Resampling.LANCZOS
)

# Resize alpha mask as well
alpha = alpha.crop(
    (
        0,
        0,
        image.width,
        image.height
    )
)

alpha = alpha.resize(
    (
        ASCII_WIDTH,
        ascii_height
    ),
    Image.Resampling.LANCZOS
)


print(
    f"ASCII grid: "
    f"{ASCII_WIDTH} x {ascii_height}"
)


# ============================================================
# GENERATE ASCII
# ============================================================

gray_pixels = list(gray.getdata())
alpha_pixels = list(alpha.getdata())

rows = []

for y in range(ascii_height):

    row = []

    for x in range(ASCII_WIDTH):

        index = y * ASCII_WIDTH + x

        brightness = gray_pixels[index]
        transparency = alpha_pixels[index]

        # Completely transparent = empty space
        if transparency < 35:
            row.append(" ")
            continue

        # Map brightness to ASCII character
        ramp_index = int(
            brightness
            / 255
            * (len(RAMP) - 1)
        )

        ramp_index = max(
            0,
            min(
                ramp_index,
                len(RAMP) - 1
            )
        )

        row.append(
            RAMP[ramp_index]
        )

    rows.append(
        "".join(row)
    )


# ============================================================
# REMOVE EMPTY ROWS
# ============================================================

while rows and not rows[0].strip():
    rows.pop(0)

while rows and not rows[-1].strip():
    rows.pop()


# ============================================================
# FIND VISIBLE ASCII BOUNDARY
# ============================================================

visible = []

for y, row in enumerate(rows):

    for x, character in enumerate(row):

        if character != " ":

            visible.append(
                (x, y)
            )


if not visible:
    raise RuntimeError(
        "ASCII conversion produced no visible characters."
    )


min_x = min(
    x for x, y in visible
)

max_x = max(
    x for x, y in visible
)

min_y = min(
    y for x, y in visible
)

max_y = max(
    y for x, y in visible
)


# Small ASCII breathing room
min_x = max(
    0,
    min_x - 1
)

max_x = min(
    ASCII_WIDTH - 1,
    max_x + 1
)

min_y = max(
    0,
    min_y - 1
)

max_y = min(
    len(rows) - 1,
    max_y + 1
)


# Crop rows and columns
rows = [
    row[min_x:max_x + 1]
    for row in rows[min_y:max_y + 1]
]


FINAL_WIDTH = max(
    len(row)
    for row in rows
)

FINAL_HEIGHT = len(rows)


print(
    f"Final ASCII: "
    f"{FINAL_WIDTH} x {FINAL_HEIGHT}"
)


# ============================================================
# SVG DIMENSIONS
# ============================================================

SVG_WIDTH = FINAL_WIDTH * CHAR_WIDTH
SVG_HEIGHT = FINAL_HEIGHT * CHAR_HEIGHT


# ============================================================
# BUILD SVG
# ============================================================

svg = []

svg.append(
    f'<svg '
    f'xmlns="http://www.w3.org/2000/svg" '
    f'width="{SVG_WIDTH}" '
    f'height="{SVG_HEIGHT}" '
    f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" '
    f'preserveAspectRatio="xMidYMid meet">'
)


# IMPORTANT:
# No background rectangle.
# The SVG is completely transparent.

svg.append(
    f'<g '
    f'font-family="Courier New, monospace" '
    f'font-size="11px" '
    f'font-weight="400" '
    f'fill="{TEXT_COLOR}">'
)


# ============================================================
# DRAW ASCII ROWS
# ============================================================

for row_index, row in enumerate(rows):

    y = (
        row_index + 1
    ) * CHAR_HEIGHT

    # Slight diagonal reveal animation
    delay = row_index * 0.025

    svg.append(
        f'<text '
        f'x="0" '
        f'y="{y}" '
        f'opacity="0">'
        f'{html.escape(row)}'

        f'<animate '
        f'attributeName="opacity" '
        f'from="0" '
        f'to="1" '
        f'dur="0.30s" '
        f'begin="{delay:.3f}s" '
        f'fill="freeze"/>'

        f'</text>'
    )


svg.append("</g>")
svg.append("</svg>")


# ============================================================
# SAVE
# ============================================================

OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


# ============================================================
# RESULT
# ============================================================

file_size = OUTPUT.stat().st_size

print()
print("================================")
print("SUCCESS!")
print("================================")
print(
    f"Created: {OUTPUT}"
)
print(
    f"File size: {file_size:,} bytes"
)
print(
    f"Final dimensions: "
    f"{SVG_WIDTH} x {SVG_HEIGHT}"
)
print(
    "Background: TRANSPARENT"
)
print(
    "Subject: AUTO-CROPPED"
)
print(
    "Alignment: CENTERED"
)
print(
    "Animation: ENABLED"
)