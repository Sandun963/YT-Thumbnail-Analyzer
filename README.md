# YouTube Thumbnail Analyzer — updated main research application

This is **Tool 3 (the main creator-facing application)**. Tool 1 collects thumbnails; Tool 2 computes the historical benchmarks. Users of this application upload **one thumbnail only**.

## Changes
- Replaced old 835-video reference ranges with **exact unrounded values from reference_summary.csv** (1,179 processed images).
- Reused the benchmark lab's **exact `engine.py` feature extraction and `assess` implementations** in `app/services/benchmark_feature_engine.py`.
- Aligned 14 feature names, image processing at 1280×720, mobile resizing at 320×180, OCR PSM 11 and minimum confidence 30, Haar face detector, edge-density clutter and numerical scales.
- The main app uses a **fixed embedded JSON reference**: `app/services/research_reference_1179.json`; it does not recompute percentiles or ask users for a ZIP.
- Text-present is informational (historical frequency), not a numerical range. Missing OCR values are not silently converted to zero.
- Retained the existing FastAPI + HTML/CSS/JS frontend and JSON report download.

## Windows setup
1. Install Python 3.10+ and Tesseract OCR separately.
2. Verify `tesseract --version` in a new terminal. If not on PATH, set environment variable `TESSERACT_CMD` to the full executable path before launching (see note below).
3. `python -m venv .venv`
4. `.venv\Scripts\activate`
5. `python -m pip install -r requirements.txt`
6. `uvicorn app.main:app --reload`
7. Open http://127.0.0.1:8000

If Tesseract is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`, run in PowerShell:
`$env:TESSERACT_CMD='C:\Program Files\Tesseract-OCR\tesseract.exe'`
then start the server.

## Verification
`python -m pytest -q`

## Research caution
Reference ranges are descriptive sample percentiles, **not optimal values**. This application does not predict CTR, future views or causal effects. Dataset selection (>50,000 views and faceless presentation) was applied during collection, not verified by this application. The reference was derived using the benchmark tool's version 1 feature formulas; do not change those formulas without regenerating the reference.

## Thesis documentation
Tool 1: YouTube channel analyzer (supporting data collection); Tool 2: benchmark lab (supporting analysis); Tool 3: this fixed-reference pre-upload analyzer (main research application).
