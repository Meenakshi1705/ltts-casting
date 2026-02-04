from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
from PIL import Image
import fitz  # PyMuPDF

# Import the new simplified casting analysis function
import sys
sys.path.append('.')
from casting import analyze_casting_image

app = FastAPI()

# 🔓 CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "input"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def convert_pdf_to_image(pdf_path):
    """Convert PDF to image if needed"""
    if pdf_path.lower().endswith('.pdf'):
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)  # Get first page
            
            zoom = 300 / 72  # 300 DPI
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Save as temporary image
            temp_image_path = pdf_path.replace('.pdf', '_temp.png')
            pix.save(temp_image_path)
            doc.close()
            
            return temp_image_path
        except Exception as e:
            print(f"Error converting PDF: {e}")
            return None
    else:
        return pdf_path  # Already an image


@app.post("/analyze")
async def analyze_casting(
    drawing_file: UploadFile = File(...),
    casting_type: str = Form(...),
    material: str = Form(...),
    volume: int = Form(...),
    process: str = Form(...),
    tolerance: str = Form("Standard"),
    surface_finish: str = Form("As-cast")
):
    """
    Receives drawing file + casting specs → runs analysis → returns result
    """
    # Save uploaded file
    file_extension = drawing_file.filename.split('.')[-1].lower()
    if file_extension not in ['pdf', 'png', 'jpg', 'jpeg']:
        return {"error": "Unsupported file type. Please upload PDF, PNG, or JPG files."}
    
    drawing_path = os.path.join(UPLOAD_DIR, drawing_file.filename)
    
    with open(drawing_path, "wb") as buffer:
        shutil.copyfileobj(drawing_file.file, buffer)

    # Prepare casting context
    casting_context = {
        "casting_type": casting_type,
        "material": material,
        "volume": volume,
        "process": process,
        "tolerance": tolerance,
        "surface_finish": surface_finish
    }

    try:
        # Convert PDF to image if needed
        image_path = convert_pdf_to_image(drawing_path)
        if image_path is None:
            return {"error": "Could not process the uploaded file."}
        
        # 🔧 Run analysis with the new simplified function
        result = analyze_casting_image(image_path, casting_context)
        
        # Clean up temporary image if created
        if image_path != drawing_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except PermissionError:
                pass  # File might still be in use, skip cleanup
        
        # Clean up uploaded file
        if os.path.exists(drawing_path):
            try:
                os.remove(drawing_path)
            except PermissionError:
                pass  # File might still be in use, skip cleanup

        return {
            "status": "success",
            "drawing_filename": drawing_file.filename,
            "casting_context": casting_context,
            "summary": result
        }
        
    except Exception as e:
        # Clean up files on error
        if 'image_path' in locals() and image_path != drawing_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except PermissionError:
                pass
        if os.path.exists(drawing_path):
            try:
                os.remove(drawing_path)
            except PermissionError:
                pass
            
        return {
            "status": "error",
            "error": str(e),
            "drawing_filename": drawing_file.filename,
            "casting_context": casting_context,
            "summary": {
                "total_checks": 0,
                "successful_evaluations": 0,
                "results": {"compliant": 0, "non_compliant": 0, "needs_review": 0},
                "output_file": None,
                "details": []
            }
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
