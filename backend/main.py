from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import base64
import os

from services.data_processing import process_file
from services.visualization import generate_charts
from services.ai_insights import get_ai_insights
from services.pdf_generator import generate_pdf_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI(title="AI Report Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Report Generator API is running"}

@app.post("/api/generate-report")
async def generate_report_endpoint(file: UploadFile = File(...), api_key: str = Form(None)):
    filename = file.filename or ""
    if not filename.lower().endswith((".csv", ".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel are supported.")

    contents = await file.read()

    summary_dict, df = process_file(contents, filename)
    if summary_dict.get("status") == "error":
        raise HTTPException(status_code=400, detail=f"Error processing data: {summary_dict.get('message')}")

    try:
        charts = generate_charts(df, summary_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {str(e)}")

    ai_text = get_ai_insights(summary_dict, api_key)

    try:
        pdf_bytes = generate_pdf_report(summary_dict, charts, ai_text, report_title="Automated Data Analysis Report")
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

    return {
        "status": "success",
        "filename": filename,
        "summary": summary_dict,
        "charts": charts,
        "ai_insights": ai_text,
        "pdf_base64": pdf_base64,
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
