from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

class LineItem(BaseModel):
    """Represents a single line item in an invoice"""
    description: str
    quantity: float
    unit_price: float
    amount: float

class Invoice(BaseModel):
    """Represents an invoice with its details"""
    invoice_number: str
    date: datetime
    vendor_name: str
    total_amount: float
    due_date: Optional[datetime] = None
    line_items: List[LineItem] = []
    status: str = "pending"
    
    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "INV-001",
                "date": "2024-03-22",
                "vendor_name": "Example Corp",
                "total_amount": "1000.00",
                "due_date": "2024-04-22",
                "line_items": [
                    {"description": "Item 1", "amount": "500.00"},
                    {"description": "Item 2", "amount": "500.00"}
                ],
                "status": "pending"
            }
        } 