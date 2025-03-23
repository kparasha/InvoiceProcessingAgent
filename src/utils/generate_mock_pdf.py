from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime, timedelta

def generate_mock_invoice():
    """Generate a mock invoice PDF for testing"""
    # Create mock_pdfs directory if it doesn't exist
    os.makedirs("data/mock_pdfs", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/mock_pdfs/mock_invoice_{timestamp}.pdf"
    
    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create content
    content = []
    
    # Add header
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    content.append(Paragraph("INVOICE", header_style))
    
    # Add company information
    company_info = [
        ["From:", "To:"],
        ["Cloudflare Inc.", "Client Company Inc."],
        ["101 Townsend St", "456 Client Ave"],
        ["San Francisco, CA 94107", "New York, NY 10001"],
        ["Phone: (888) 99-FLARE", "Phone: (555) 987-6543"],
        ["Email: billing@cloudflare.com", "Email: accounts@client.com"]
    ]
    
    company_table = Table(company_info, colWidths=[3*inch, 3*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    content.append(company_table)
    content.append(Spacer(1, 20))
    
    # Add invoice details
    invoice_number = f"INV-{timestamp}"
    current_date = datetime.now()
    due_date = current_date + timedelta(days=30)
    
    details = [
        ["Invoice Number:", invoice_number],
        ["Date:", current_date.strftime("%B %d, %Y")],
        ["Due Date:", due_date.strftime("%B %d, %Y")]
    ]
    
    details_table = Table(details, colWidths=[1.5*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    content.append(details_table)
    content.append(Spacer(1, 20))
    
    # Add line items
    line_items = [
        ["Description", "Quantity", "Unit Price", "Amount"],
        ["Consulting Services", "40", "$150.00", "$6,000.00"],
        ["Software Development", "60", "$200.00", "$12,000.00"],
        ["Project Management", "20", "$175.00", "$3,500.00"],
        ["", "", "Subtotal:", "$21,500.00"],
        ["", "", "Tax (10%):", "$2,150.00"],
        ["", "", "Total:", "$23,650.00"]
    ]
    
    items_table = Table(line_items, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
    ]))
    content.append(items_table)
    content.append(Spacer(1, 30))
    
    # Add terms and conditions
    terms = [
        "Terms and Conditions:",
        "1. Payment is due within 30 days of invoice date",
        "2. Late payments will incur a 5% fee",
        "3. All prices are in USD",
        "4. This invoice is subject to our standard terms of service"
    ]
    
    for term in terms:
        content.append(Paragraph(term, styles['Normal']))
    
    # Build the PDF
    doc.build(content)
    print(f"Generated mock invoice: {filename}")

if __name__ == "__main__":
    generate_mock_invoice() 