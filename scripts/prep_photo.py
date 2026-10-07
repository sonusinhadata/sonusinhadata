from pathlib import Path
import sys

import cv2
import numpy as np
from rembg import remove


def prepare_photo(input_file):
    input_path = Path(input_file)
    output_path = Path("source-prepped.png")

    print(f"Input image: {input_path}")
    print("Checking input file...")

    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        return

    if input_path.stat().st_size == 0:
        print("ERROR: Input image is empty.")
        return

    print("Removing background...")

    try:
        with open(input_path, "rb") as f:
            original = f.read()
        result = remove(original)
        temp_path = Path("temp-no-bg.png")

        with open(temp_path, "wb") as f:
            f.write(result)

        print("Background removed successfully.")
    except Exception as e:
        print(f"ERROR during background removal: {e}")
        return
    print("Reading processed image...")
    image = cv2.imread(
        str(temp_path),
        cv2.IMREAD_UNCHANGED
    )
    if image is None:
        print("ERROR: OpenCV could not read the processed image.")
        return
    
    print("Enhancing image...")
    if len(image.shape) == 3 and image.shape[2] == 4:
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
        gray = cv2.cvtColor(
            bgr,
            cv2.COLOR_BGR2GRAY
        )
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
        gray = clahe.apply(gray)
        background = np.full_like(
            gray,
            255
        )
        mask = alpha > 10
        final = background.copy()
        final[mask] = gray[mask]
    else:
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
        final = clahe.apply(gray)
    cv2.imwrite(
        str(output_path),
        final
    )
    temp_path.unlink(
        missing_ok=True
    )
    print()
    print("SUCCESS!")
    print(f"Created: {output_path}")
    size = output_path.stat().st_size
    print(f"Output size: {size:,} bytes")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: "
            "python scripts\\prep_photo.py source-photo.png"
        )
        sys.exit(1)
    prepare_photo(sys.argv[1])