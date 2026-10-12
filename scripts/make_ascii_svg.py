from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np
import html

try:
    from scipy import ndimage
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ============================================================
# CONFIGURATION
# ============================================================

INPUT = Path("source-photo.png")
OUTPUT = Path("sonu-ascii.svg")

ASCII_WIDTH = 58          # resolution of the ASCII portrait
CHAR_WIDTH = 6
CHAR_HEIGHT = 7
FONT_SIZE = 8
CROP_MARGIN = 4           # px margin around subject in source image

ALPHA_THRESHOLD = 160     # alpha >= this counts as "visible"
BG_TOLERANCE = 40         # colour distance from background to count as subject
TEXT_COLOR = "#39d353"

# Dark -> dense, light -> sparse.
# NO trailing space: empty space is ONLY used outside the portrait mask.
RAMP = "@%#*+=-:."


# ============================================================
# LOAD IMAGE
# ============================================================

if not INPUT.exists():
    raise FileNotFoundError(f"Could not find source image: {INPUT}")

image = Image.open(INPUT).convert("RGBA")
print(f"Original image: {image.width} x {image.height}")

rgba = np.array(image)
rgb = rgba[:, :, :3].astype(int)
alpha = rgba[:, :, 3]


# ============================================================
# BUILD SUBJECT MASK
# ============================================================

mask = alpha >= ALPHA_THRESHOLD

# If almost everything is "visible", the background is NOT truly
# transparent (this is what caused the dotted rows). Remove it by
# comparing every pixel with the background colour (taken from corners).
if mask.mean() > 0.90:
    print("Background is not transparent -> using colour-based removal")
    h, w = mask.shape
    corners = np.array([
        rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]
    ])
    bg_color = np.median(corners, axis=0)
    distance = np.abs(rgb - bg_color).max(axis=2)
    mask = distance > BG_TOLERANCE

# Keep only the largest blob (the head) and fill holes inside it.
if HAS_SCIPY:
    labels, count = ndimage.label(mask)
    if count > 1:
        sizes = ndimage.sum(mask, labels, range(1, count + 1))
        mask = labels == (np.argmax(sizes) + 1)
    mask = ndimage.binary_fill_holes(mask)
else:
    print("Tip: run `pip install scipy` for cleaner stray-pixel removal")

if not mask.any():
    raise RuntimeError("No visible subject found in source-photo.png.")


# ============================================================
# TIGHT CROP AROUND THE SUBJECT
# ============================================================

ys, xs = np.where(mask)
left = max(0, xs.min() - CROP_MARGIN)
right = min(image.width, xs.max() + 1 + CROP_MARGIN)
top = max(0, ys.min() - CROP_MARGIN)
bottom = min(image.height, ys.max() + 1 + CROP_MARGIN)

image = image.crop((left, top, right, bottom))
mask_img = Image.fromarray((mask * 255).astype("uint8")).crop(
    (left, top, right, bottom)
)

print(f"Cropped portrait: {image.width} x {image.height}")


# ============================================================
# GRAYSCALE + CONTRAST
# ============================================================

gray = image.convert("RGB").convert("L")
gray = ImageEnhance.Contrast(gray).enhance(1.30)


# ============================================================
# RESIZE TO ASCII GRID
# ============================================================

aspect_ratio = gray.height / gray.width
ascii_height = max(1, round(ASCII_WIDTH * aspect_ratio * 0.50))

gray = gray.resize((ASCII_WIDTH, ascii_height), Image.Resampling.LANCZOS)
mask_small = mask_img.resize((ASCII_WIDTH, ascii_height), Image.Resampling.LANCZOS)

gray_px = np.array(gray)
mask_px = np.array(mask_small) >= 128


# ============================================================
# ASCII CONVERSION
# ============================================================

rows = []
for y in range(ascii_height):
    row = []
    for x in range(ASCII_WIDTH):
        if not mask_px[y, x]:
            row.append(" ")
        else:
            idx = int(gray_px[y, x] / 255 * (len(RAMP) - 1))
            row.append(RAMP[max(0, min(idx, len(RAMP) - 1))])
    rows.append("".join(row))


# ============================================================
# CROP GRID TO REAL PORTRAIT BOUNDS
# ============================================================

grid_ys, grid_xs = np.where(mask_px)
min_x, max_x = grid_xs.min(), grid_xs.max()
min_y, max_y = grid_ys.min(), grid_ys.max()

rows = [row[min_x:max_x + 1] for row in rows[min_y:max_y + 1]]

final_width = max_x - min_x + 1
final_height = len(rows)
print(f"Final ASCII: {final_width} x {final_height}")


# ============================================================
# CREATE SVG (canvas == portrait size -> perfectly centred,
# zero transparent margin)
# ============================================================

svg_width = final_width * CHAR_WIDTH
svg_height = final_height * CHAR_HEIGHT

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{svg_width}" height="{svg_height}" '
    f'viewBox="0 0 {svg_width} {svg_height}" '
    f'preserveAspectRatio="xMidYMid meet">',
    f'<g font-family="Courier New, monospace" '
    f'font-size="{FONT_SIZE}px" fill="{TEXT_COLOR}">',
]

for row_index, row in enumerate(rows):
    stripped = row.strip(" ")
    if not stripped:
        continue

    # Leading spaces are NOT trusted (SVG collapses them), so we
    # position each row explicitly with an x offset instead.
    lead = len(row) - len(row.lstrip(" "))
    x = lead * CHAR_WIDTH
    y = (row_index + 1) * CHAR_HEIGHT
    text_len = len(stripped) * CHAR_WIDTH

    svg.append(
        f'<text x="{x}" y="{y}" textLength="{text_len}" '
        f'lengthAdjust="spacing" xml:space="preserve">'
        f'{html.escape(stripped)}</text>'
    )

svg.extend(["</g>", "</svg>"])

OUTPUT.write_text("\n".join(svg), encoding="utf-8")

print(f"Created: {OUTPUT}  ({svg_width} x {svg_height})")