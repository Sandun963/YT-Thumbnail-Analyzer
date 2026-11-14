"""Main application: image upload -> shared feature extraction -> fixed references."""
import io
import math
from PIL import Image, UnidentifiedImageError
from app.services.feature_extraction import extract_features, FEATURES
from app.services.benchmark_engine import compare, REFERENCE

MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 20_000_000

def analyze_thumbnail_bytes(content: bytes, filename: str = "thumbnail"):
    if not content or len(content) > MAX_BYTES:
        raise ValueError("Image must be between 1 byte and 10 MB.")
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
        with Image.open(io.BytesIO(content)) as image:
            fmt = image.format
            width, height = image.size
            if width * height > MAX_PIXELS:
                raise ValueError("Image dimensions exceed 20 megapixels.")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("File is not a supported image.") from exc
    if fmt not in ("JPEG", "PNG", "WEBP"):
        raise ValueError("Only JPG, PNG and WebP images are supported.")
    # Crucial: analyze original encoded bytes using EXACTLY the same decoder,
    # resizing, OCR, face detection and formulas as the historical benchmark.
    try:
        raw = extract_features(content)
    except Exception as exc:
        raise ValueError(f"Thumbnail feature extraction failed: {exc}") from exc
    clean = {k: (float(v) if isinstance(v, (int, float)) and math.isfinite(float(v)) else None) for k,v in raw.items()}
    comparisons = compare(clean)
    return {
        "filename": filename,
        "image": {"width": width, "height": height, "format": fmt},
        "features": clean,
        "benchmarks": comparisons,
        "reference": {"version":REFERENCE["version"], "sample_size":REFERENCE["sample_size_processed"], "bootstrap_iterations":REFERENCE["bootstrap_iterations"]},
        "summary": {
            "within":sum(x["status"] == "within" for x in comparisons),
            "outside":sum(x["status"] in ("below","above") for x in comparisons),
            "unavailable":sum(x["status"] == "unavailable" for x in comparisons),
            "informational":sum(x["status"] == "informational" for x in comparisons)
        },
        "research_note":""
    }
