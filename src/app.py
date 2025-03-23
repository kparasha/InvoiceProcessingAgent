from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
from datetime import datetime
import logging
from src.agents.extraction_agent import ExtractionAgent
from src.agents.validation_agent import ValidationAgent
from src.agents.scraping_agent import ScrapingAgent
from src.utils.pdf_processor import PDFProcessor
from src.utils.models import Invoice
from src.services.voice_service import VoiceService
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/invoice_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Invoice Processing System")

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/templates")

# Initialize agents and services
extraction_agent = ExtractionAgent()
validation_agent = ValidationAgent()
scraping_agent = ScrapingAgent()
voice_service = VoiceService()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    try:
        # Generate a unique filename with timestamp and random ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{timestamp}_{unique_id}_{file.filename}"
        file_path = os.path.join("uploads", filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process PDF
        pdf_processor = PDFProcessor(file_path)
        invoice_text = pdf_processor.extract_text()
        
        # Extract data
        invoice_data = extraction_agent.extract_invoice_data(invoice_text)
        logger.info(f"Extracted invoice data: {invoice_data}")
        
        # Validate invoice
        validation_result = validation_agent.validate_invoice(invoice_data)
        logger.info(f"Validation result: {validation_result}")
        
        # Get vendor information
        vendor_info = scraping_agent.scrape_vendor_info(invoice_data['vendor_name'])
        logger.info(f"Vendor information: {vendor_info}")
        
        # Generate voice notification
        audio_url = None
        if validation_result['is_valid']:
            try:
                notification_msg = f"New valid invoice received from {invoice_data['vendor_name']} for ${invoice_data['total_amount']}"
                audio_url = voice_service.notify_finance_manager(notification_msg)
                if audio_url:
                    logger.info(f"Generated voice notification: {audio_url}")
                else:
                    logger.warning("Voice notification generation skipped or failed")
            except Exception as e:
                logger.error(f"Error generating voice notification: {str(e)}")
                audio_url = None
        
        # Cleanup
        try:
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")
        
        # Return results
        return {
            "invoice_data": invoice_data,
            "validation_result": validation_result,
            "vendor_info": vendor_info,
            "audio_url": audio_url
        }
        
    except Exception as e:
        logger.error(f"Error processing invoice: {str(e)}")
        if 'file_path' in locals():
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-invoice")
async def process_invoice(invoice_text: str = Form(...)):
    """
    Process an invoice and return extracted data, validation results, and vendor information
    """
    try:
        # Extract invoice data
        invoice = extraction_agent.extract_invoice_data(invoice_text)
        
        # Validate invoice
        validation_result = validation_agent.validate_invoice(invoice)
        
        # Get vendor information
        vendor_info = scraping_agent.scrape_vendor_info(invoice.vendor_name)
        
        return {
            "invoice_data": {
                "invoice_number": invoice.invoice_number,
                "date": str(invoice.date),
                "vendor_name": invoice.vendor_name,
                "total_amount": str(invoice.total_amount),
                "due_date": str(invoice.due_date) if invoice.due_date else None,
                "line_items": invoice.line_items
            },
            "validation_result": validation_result,
            "vendor_info": vendor_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True) 