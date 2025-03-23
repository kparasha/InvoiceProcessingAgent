import os
from pathlib import Path
from PyPDF2 import PdfReader
from fastapi import UploadFile, HTTPException
from typing import Optional, Dict, Any

class PDFProcessor:
    def __init__(self, file_path: str):
        """Initialize with a file path instead of directory"""
        self.file_path = Path(file_path)
        self.upload_dir = self.file_path.parent
        # Only create directory, don't try to create the file
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_pdf(self, file: UploadFile) -> Path:
        """Save uploaded PDF file"""
        file_path = self.upload_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return file_path

    @staticmethod
    def validate_pdf(file: UploadFile) -> bool:
        """
        Validates if the uploaded file is a valid PDF.
        
        Args:
            file: The uploaded file to validate
            
        Returns:
            bool: True if the file is a valid PDF, False otherwise
            
        Raises:
            HTTPException: If the file is not a PDF or is corrupted
        """
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
            
        try:
            # Try to read the PDF to validate it
            reader = PdfReader(file.file)
            if len(reader.pages) == 0:
                raise HTTPException(status_code=400, detail="PDF file is empty")
            return True
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")
        finally:
            # Reset file pointer
            file.file.seek(0)
    
    def extract_text(self) -> str:
        """Extract text from PDF file"""
        try:
            with open(self.file_path, 'rb') as file:
                pdf = PdfReader(file)
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    def process_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process PDF file and return extracted information
        
        Args:
            file: The uploaded PDF file
            
        Returns:
            Dict[str, Any]: Dictionary containing processed PDF information
        """
        # Validate the PDF
        self.validate_pdf(file)
        
        # Save the file
        file_path = self.save_pdf(file)
        
        # Extract text
        text = self.extract_text()
        
        return {
            "filename": file.filename,
            "file_path": str(file_path),
            "text": text,
            "page_count": len(PdfReader(file_path).pages)
        } 