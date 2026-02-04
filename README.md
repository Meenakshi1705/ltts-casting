# Casting Design Assistant

An AI-powered application for automated casting drawing analysis and validation. Combines a Python backend (FastAPI) with a React/Vite frontend for interactive casting design evaluation.

## Project Layout

```
casting/
├── backend/                           # FastAPI backend
│   ├── main.py                        # API endpoints and PDF-to-image conversion
│   └── rule_engine.py                 # Legacy rule engine module
├── frontend/casting-assistant/        # React/Vite web UI
│   ├── src/
│   │   ├── api/castingApi.js          # API client for backend communication
│   │   ├── components/
│   │   │   ├── FileUpload.jsx         # File upload and casting specs form
│   │   │   └── ResultView.jsx         # Results display and analysis summary
│   │   └── index.css                  # Styling
│   └── package.json
├── input/
│   └── rules.json                     # 22 casting design rules
├── output/                            # Generated Excel analysis reports
├── casting.py                         # CLI entry point with Gemini AI integration
├── casting_config.py                  # Material properties and helpers
├── req.txt                            # Python dependencies
├── .env.example                       # Environment variables template
└── README.md
```

## Features

- **Single Drawing Upload**: Upload PDF, PNG, or JPG engineering drawings
- **Casting Parameters**: Specify casting type, material, volume, process, tolerance, and surface finish
- **AI Analysis**: Uses Google Generative AI (Gemini) to analyze drawings against 22 casting design rules
- **Excel Reports**: Generates detailed analysis reports with compliance status and recommendations
- **REST API**: FastAPI backend with CORS support for web frontend
- **Interactive UI**: React/Vite frontend for easy user interaction

## Prerequisites

- Python 3.8+
- Node.js/npm (for frontend development)
- Install Python packages:

```powershell
python -m pip install -r req.txt
```

## Environment Setup

1. Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

2. Add your Gemini API key to `.env`:

```powershell
$env:GEMINI_API_KEY = 'your_gemini_api_key_here'
```

## Running the Application

### Backend (FastAPI)

```powershell
# From repo root
python -m uvicorn backend.main:app --reload --host localhost --port 8000
```

### Frontend (React/Vite)

```powershell
cd frontend/casting-assistant
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` (or `http://localhost:5174` as fallback).

## API Endpoints

### POST `/analyze`
Analyzes a casting drawing against design rules.

**Request:**
- `drawing_file` (file): PDF, PNG, or JPG drawing
- `casting_type` (string): Type of casting process
- `material` (string): Material specification
- `volume` (int): Production volume
- `process` (string): Manufacturing process
- `tolerance` (string): Tolerance specification
- `surface_finish` (string): Surface finish requirement

**Response:**
```json
{
  "status": "success",
  "drawing_filename": "drawing.pdf",
  "casting_context": { ... },
  "summary": {
    "total_checks": 22,
    "successful_evaluations": 22,
    "results": {
      "compliant": 18,
      "non_compliant": 2,
      "needs_review": 2
    },
    "output_file": "casting_analysis_..._timestamp.xlsx",
    "details": [ ... ]
  }
}
```

### GET `/latest-report`
Retrieves the most recent analysis report.

### GET `/download/{filename}`
Downloads a generated Excel report file.

### GET `/health`
Health check endpoint.

## Implementation Details

- **PDF Conversion**: Uses PyMuPDF (fitz) to convert PDFs to high-resolution images (300 DPI)
- **AI Analysis**: `casting.py` uses Google Generative AI with structured prompts for JSON parsing
- **Excel Generation**: `openpyxl` for report formatting, `pandas` for data assembly
- **API Integration**: FastAPI with CORS middleware for cross-origin requests from frontend

## Key Files

- `casting.py` - Main CLI and AI analysis logic with `analyze_casting_image()` function
- `backend/main.py` - FastAPI routes, file handling, PDF conversion
- `frontend/casting-assistant/src/api/castingApi.js` - API client wrapper
- `input/rules.json` - 22 casting design rules database
- `casting_config.py` - Material properties and configuration helpers


```powershell
# Install deps once
python -m pip install -r req.txt

```
Outputs
- Generated reports are written to the `output/` directory as an `.xlsx` file named like `casting_analysis_<material>_<volume>parts_<timestamp>.xlsx`.
- Converted PDF pages are saved to `images/` by default.

Known issues / Notes
- `pdf2image` requires poppler (system dependency) and may fail if not installed.
- Vertex AI usage: the repo uses a `GenerativeModel` and `Part.from_data`. Ensure your environment, project, and permissions are configured before running.


Contact / Help
- If you'd like, I can:
  # Casting Design Assistant

  Command-line toolkit and small frontend for automated casting drawing checklist analysis using a generative AI backend.

  **Current project layout (root of repo)**

  - `.env.example` - example environment file for local secrets.
  - `casting.py` - current main CLI entrypoint (uses `google-generativeai` / Gemini). Prompts for an image/PDF and casting parameters and writes an Excel report to `output/`.
  - `casting_config.py` - material properties, guidance helpers, and filename helpers used by the scripts.
  - `backend/` - backend module (contains `rule_engine.py` and other helpers used in prior iterations).
  - `frontend/` - React/Vite frontend live in `frontend/casting-assistant/`.
  - `input/` - input assets (example rules, Excel samples, etc.). `casting.py` currently expects a JSON rules file at `input/rules.json` by default.
  - `output/` - program output (generated Excel reports).
  - `images/` - image outputs (converted from PDFs or saved temporary images).
  - `req.txt` - Python package dependencies list.
  - `README.md` - this file.

  Notes about the code
  - `casting.py` is the active entrypoint. It uses `google.generativeai` (Gemini) and expects `GEMINI_API_KEY` set as an environment variable (or in a `.env` file). It loads rules from `input/rules.json` and accepts a single drawing (PDF or image).
  - Older versions / experimental scripts (`v1.py`, `v1_c.py`) may exist in the repo history or worktree; they used `vertexai` or other flows. The current, tested script is `casting.py`.

  Prerequisites
  - Python 3.8+
  - System dependency: PyMuPDF is used for PDF→image conversion (no separate poppler install required when using PyMuPDF). If you later switch to `pdf2image`, you'll need poppler.

  Install Python packages
  ```powershell
  python -m pip install -r req.txt
  ```

  Environment
  - Copy `.env.example` to `.env` and set values as needed, or set env vars directly.
  - The main script requires `GEMINI_API_KEY` in the environment. Example (PowerShell):

  ```powershell
  $env:GEMINI_API_KEY = 'your_api_key_here'
  ```

  Usage
  - Run the main CLI that analyzes a single drawing file:

  ```powershell
  # From repo root
  python casting.py
  ```

  The script will prompt for:
  - Path to drawing file (PDF/PNG/JPG). PDFs are converted to a temporary PNG of the first page.
  - Casting type, material, production volume, process, tolerance, and surface finish.

  Outputs
  - Excel reports are written to the `output/` directory with names like `casting_analysis_<material>_<volume>parts_<timestamp>.xlsx`.

  Key implementation details
  - AI integration: `casting.py` uses `google.generativeai` (Gemini) and builds structured prompts requesting JSON output. The helper `extract_json_from_response()` tries to robustly parse JSON from model responses.
  - Rules: by default `casting.py` loads rules from `input/rules.json`. The expected JSON structure is an array of rule objects; see `casting.py`'s `load_rules_from_json()` for the exact fields used.

  Testing and development
  - There's a `test_analysis.py` placeholder/test harness in the repo you can extend for unit tests.

  Known issues & suggested cleanups
  - If you have multiple rule sources (Excel vs JSON) we can add a CLI flag `--rules` to accept either JSON or Excel and unify the loaders.
  - Some older scripts in the repo used `vertexai` vs `google-generativeai`; consider standardizing on one client library depending on your target deployment.

  Next steps I can help with
  - Update `input/rules.json` example or add an example Excel file in `input/`.
  - Add a small CLI wrapper to support `--rules path` and automatically pick JSON vs Excel.
  - Add unit tests for rule loading and the PDF→image conversion flow.

  If you'd like, tell me which of the next steps to take and I will implement it.
