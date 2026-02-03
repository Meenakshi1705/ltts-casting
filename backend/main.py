from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
from typing import List

from backend.rule_engine import run_casting_analysis

app = FastAPI()

# 🔓 CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "input"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/analyze")
async def analyze_casting(
    excel_file: UploadFile = File(...),
    pdf_file: UploadFile = File(...),
    casting_type: str = Form(...),
    material: str = Form(...),
    volume: int = Form(...),
    process: str = Form(...),
    tolerance: str = Form("Standard"),
    surface_finish: str = Form("As-cast")
):
    """
    Receives Excel rules + PDF drawing + casting specs → runs analysis → returns result
    """
    # Save uploaded files
    excel_path = os.path.join(UPLOAD_DIR, excel_file.filename)
    pdf_path = os.path.join(UPLOAD_DIR, pdf_file.filename)
    
    with open(excel_path, "wb") as buffer:
        shutil.copyfileobj(excel_file.file, buffer)
    
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(pdf_file.file, buffer)

    # Prepare casting context
    casting_context = {
        "casting_type": casting_type,
        "material": material,
        "volume": volume,
        "process": process,
        "tolerance": tolerance,
        "surface_finish": surface_finish
    }

    # 🔧 Run analysis with both files
    result = run_casting_analysis(excel_path, pdf_path, casting_context, OUTPUT_DIR)

    return {
        "status": "success",
        "excel_filename": excel_file.filename,
        "pdf_filename": pdf_file.filename,
        "casting_context": casting_context,
        "summary": result
    }


@app.get("/latest-report")
async def get_latest_report():
    """Get the most recent analysis report"""
    try:
        import glob
        files = glob.glob(os.path.join(OUTPUT_DIR, "casting_analysis_*.xlsx"))
        if files:
            latest_file = max(files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return {"filename": filename, "path": f"/download/{filename}"}
        return {"error": "No reports found"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/download/{filename}")
async def download_result(filename: str):
    """Download generated Excel result file"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    return {"error": "File not found"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Casting Analysis API is running"}
