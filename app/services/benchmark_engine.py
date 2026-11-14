"""Compare thumbnail measurements with fixed historical reference values."""
import json
import math
import numbers
from pathlib import Path
from app.services.benchmark_feature_engine import assess, FEATURES, CONFIG, VERSION

REFERENCE_PATH = Path(__file__).with_name("research_reference_1179.json")
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
if REFERENCE.get("version") != VERSION or REFERENCE.get("config") != CONFIG:
    raise RuntimeError("Embedded reference incompatible with current feature extraction configuration")

LABELS = {
    "brightness": "Brightness", "contrast": "Contrast",
    "sharpness": "Sharpness", "mobile_sharpness": "Mobile sharpness",
    "ocr_text_percentage": "OCR text coverage", "ocr_confidence": "OCR confidence",
    "text_word_count": "Detected word count", "text_median_height": "Text median height",
    "text_local_contrast": "Text local contrast", "text_center_x": "Text horizontal centre",
    "text_present": "OCR text detected", "face_percentage": "Detected face area",
    "face_count": "Detected face count", "clutter_score": "Edge-density clutter"
}
UNITS = {"ocr_text_percentage":"%", "face_percentage":"%"}

def json_number(value):
    """Convert pandas/NumPy missing or non-finite numbers to JSON null."""
    if value is None:
        return None
    if isinstance(value, numbers.Real):
        numeric = float(value)
        return numeric if math.isfinite(numeric) else None
    return None


def compare(features):
    rows = assess(features, REFERENCE).to_dict(orient="records")
    results = []
    for row in rows:
        name = row["feature"]
        status = row["assessment"]
        value = json_number(row["value"])
        low, med, high = (json_number(row[key]) for key in ("p10", "median", "p90"))
        note = row["feedback"]
        if name == "brightness" and status == "below reference":
            note += " Check whether important subjects remain visible at small display sizes."
        elif name == "mobile_sharpness" and status == "below reference":
            note += " Inspect fine details in a reduced-size preview."
        elif name == "ocr_text_percentage" and status == "above reference":
            note += " Consider reviewing text density and readability."
        elif name == "text_word_count" and status == "above reference":
            note += " Check whether the wording can be simplified without losing meaning."
        elif name == "clutter_score" and status == "above reference":
            note += " Review visual complexity; this is an edge-density proxy, not perceived clutter."
        elif name in ("face_count", "face_percentage"):
            note += " Facial imagery is not required for a faceless video."
        results.append({
            "feature": name, "label": LABELS[name],
            "value": value,
            "unit": UNITS.get(name, ""),
            "range": {"lower":low,"median":med,"upper":high} if low is not None and high is not None else None,
            "status": ("within" if status == "within reference" else
                       "below" if status == "below reference" else
                       "above" if status == "above reference" else
                       "informational" if name == "text_present" else "unavailable"),
            "explanation": note
        })
    return results
