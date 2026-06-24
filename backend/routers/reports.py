import os
from fastapi import APIRouter
from fpdf import FPDF
from .. import schemas
from ..logger import logger

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORTS_DIR = "static/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/generate-report")
def generate_report(request: schemas.ReportRequest):
    logger.info(f"Generating report for {request.city_name}")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt=f"Urban Heat Intelligence Report: {request.city_name}", ln=1, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Data Summary:", ln=1)
    
    for key, value in request.data_summary.items():
        pdf.cell(200, 10, txt=f"- {key}: {value}", ln=1)
        
    pdf.cell(200, 10, txt="\nRecommendations are based on the above risk profile.", ln=1)
    
    file_name = f"{request.city_name.lower().replace(' ', '_')}_report.pdf"
    file_path = os.path.join(REPORTS_DIR, file_name)
    pdf.output(file_path)
    
    return {
        "city_name": request.city_name,
        "report_url": f"/static/reports/{file_name}",
        "message": "Report generated successfully."
    }

