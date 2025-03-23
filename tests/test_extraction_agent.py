import pytest
from src.agents.extraction_agent import ExtractionAgent
from src.utils.models import Invoice
from datetime import date
from decimal import Decimal

def test_extraction_agent():
    # Sample invoice text
    invoice_text = """
    INVOICE #INV-001
    Date: 2024-03-22
    Vendor: Example Corp
    Due Date: 2024-04-22
    
    Description          Amount
    Item 1              $500.00
    Item 2              $500.00
    -------------------------
    Total:              $1000.00
    """
    
    agent = ExtractionAgent()
    invoice = agent.extract_invoice_data(invoice_text)
    
    assert isinstance(invoice, Invoice)
    assert invoice.invoice_number == "INV-001"
    assert invoice.date == date(2024, 3, 22)
    assert invoice.vendor_name == "Example Corp"
    assert invoice.total_amount == Decimal("1000.00")
    assert invoice.due_date == date(2024, 4, 22)
    assert len(invoice.line_items) == 2 