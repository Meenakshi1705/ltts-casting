# Casting Design Assistant

Small command-line toolkit for automated casting drawing checklist analysis using an AI backend.

**Project layout**

- `casting.py`, `casting_config.py` - helpers and configuration for material/property guidance and filename helpers.
- `backend/` - small backend module (contains `rule_engine.py` used by earlier iterations).
- `frontend/casting-assistant/` - web frontend (React/Vite) for interactive UI.
- `input/` - input assets (e.g., Excel checklist sample).
- `output/` - program output (generated Excel reports).
- `images/` - image outputs (generated from PDFs).
- `rules/` - (expected) JSON rules file location used by `v1_c.py`.

Quick notes:
- The repository uses Vertex AI (`vertexai`) to call a generative model; the code expects `vertexai` and `vertexai.generative_models` to be available.
- PDF processing uses `pdf2image` and `poppler` (system dependency) to convert pages to PNG.
- Excel outputs are built with `openpyxl`; data manipulation uses `pandas`.

Prerequisites
- Python 3.8+
- Install Python dependencies from `req.txt`:

```powershell
python -m pip install -r req.txt
```

- poppler (Windows): download Poppler for Windows and add its `bin` folder to `PATH` so `pdf2image` can call it.
- Google/Vertex AI credentials (if using the Vertex AI model locally): ensure you are authenticated and any required env vars/keys are set. The scripts set `PROJECT_ID` and `GEMINI_LOCATION` in the source; adapt as needed.

Environment
- There is an `.env.example` in the project root — copy to `.env` and edit if you want to manage secrets locally.
- If using Google Cloud credentials, set `GOOGLE_APPLICATION_CREDENTIALS` appropriately in your environment.

Usage
- From project root (where `v1.py` / `v1_c.py` live), run:

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

Development / Next steps
- Fix the unreachable code block inside `v1.py`'s Excel loader (I can patch it now).
- Add unit tests for rule loading and PDF conversion (there is `test_analysis.py` as a starter).

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
