import io
import json
import numpy as np
import cv2
import pytest
from app.services.benchmark_engine import REFERENCE, compare
from app.services.benchmark_feature_engine import CONFIG, FEATURES, VERSION, extract_features
from app.services.thumbnail_analyzer import analyze_thumbnail_bytes

def test_reference_version_and_features():
    assert REFERENCE["version"] == VERSION
    assert REFERENCE["config"] == CONFIG
    assert REFERENCE["sample_size_processed"] == 1179
    assert set(REFERENCE["features"]) == set(FEATURES)
    assert len(FEATURES) == 14

def test_assessment_boundaries():
    vals = {k: 0.0 for k in FEATURES}
    vals["brightness"] = REFERENCE["features"]["brightness"]["p10"]
    assert next(r for r in compare(vals) if r["feature"] == "brightness")["status"] == "within"
    vals["brightness"] -= 0.00001
    assert next(r for r in compare(vals) if r["feature"] == "brightness")["status"] == "below"
    vals["brightness"] = REFERENCE["features"]["brightness"]["p90"] + 0.00001
    assert next(r for r in compare(vals) if r["feature"] == "brightness")["status"] == "above"

def test_no_text_is_informational_and_missing_ocr_unavailable():
    vals = {k: 0.0 for k in FEATURES}
    vals["text_present"] = 0
    vals["ocr_confidence"] = None
    rows = {r["feature"]:r for r in compare(vals)}
    assert rows["text_present"]["status"] == "informational"
    assert rows["ocr_confidence"]["status"] == "unavailable"

def test_end_to_end_image(monkeypatch):
    import app.services.benchmark_feature_engine as engine
    # Mock OCR only: exercise real image processing, detector and assessment.
    monkeypatch.setattr(engine.pytesseract, "image_to_data", lambda *a, **kw: {
        "text": [], "conf": [], "left": [], "top": [], "width": [], "height": []
    })
    image = np.full((720,1280,3), 128, dtype=np.uint8)
    ok, enc = cv2.imencode(".png", image)
    assert ok
    result = analyze_thumbnail_bytes(enc.tobytes(), "test.png")
    assert len(result["features"]) == 14
    assert len(result["benchmarks"]) == 14
    assert result["features"]["brightness"] == pytest.approx(128/255)
    assert result["features"]["text_present"] == 0
    assert result["features"]["ocr_confidence"] is None

def test_invalid_image_rejected():
    with pytest.raises(ValueError):
        analyze_thumbnail_bytes(b"not an image", "bad.png")


def test_missing_ocr_is_strict_json_serializable():
    vals = {k: 0.0 for k in FEATURES}
    vals["text_present"] = 0
    for key in ("ocr_confidence", "text_median_height", "text_local_contrast", "text_center_x"):
        vals[key] = None
    result = compare(vals)
    assert all(row["value"] is None for row in result if row["feature"] in ("ocr_confidence", "text_median_height", "text_local_contrast", "text_center_x"))
    json.dumps(result, allow_nan=False)

def test_real_response_is_strict_json_serializable(monkeypatch):
    import app.services.benchmark_feature_engine as engine
    monkeypatch.setattr(engine.pytesseract, "image_to_data", lambda *a, **kw: {
        "text": [], "conf": [], "left": [], "top": [], "width": [], "height": []
    })
    image = np.full((720, 1280, 3), 128, dtype=np.uint8)
    ok, enc = cv2.imencode(".png", image)
    assert ok
    result = analyze_thumbnail_bytes(enc.tobytes(), "test.png")
    json.dumps(result, allow_nan=False)
