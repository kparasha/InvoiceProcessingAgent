from src.agents.extraction_agent import ExtractionAgent
from src.agents.validation_agent import ValidationAgent
from src.agents.scraping_agent import ScrapingAgent
import sys

def main():
    # Sample invoice text
    invoice_text = """
    INVOICE

    Invoice Number: INV-2024-001
    Date: March 22, 2024

    FROM:
    Cloudflare, Inc.
    101 Townsend St
    San Francisco, CA 94107

    BILL TO:
    AI Agents Inc.
    123 Tech Lane
    Silicon Valley, CA 94025

    DUE DATE: April 22, 2024

    LINE ITEMS:
    1. Consulting Services - Q1 2024        $2,500.00
    2. Development Work - March 2024        $1,750.00
    3. Project Management - March 2024      $1,250.00

    SUBTOTAL:   $5,500.00
    TAX (8.5%): $467.50
    TOTAL:      $5,967.50

    Please make payment within 30 days.
    """

    try:
        print("\nExtracting invoice data...")
        extraction_agent = ExtractionAgent()
        invoice = extraction_agent.extract_invoice_data(invoice_text)
        
        print("\nExtracted Invoice Data:")
        print(f"Invoice Number: {invoice.invoice_number}")
        print(f"Date: {invoice.date}")
        print(f"Vendor: {invoice.vendor_name}")
        print(f"Total Amount: ${invoice.total_amount}")
        print(f"Due Date: {invoice.due_date}")
        print("\nLine Items:")
        for item in invoice.line_items:
            print(f"- {item['description']}: ${item['amount']}")
            
        print("\nValidating invoice...")
        validation_agent = ValidationAgent()
        validation_result = validation_agent.validate_invoice(invoice)
        
        print("\nValidation Results:")
        print(f"Status: {'Valid' if validation_result['is_valid'] else 'Invalid'}")
        if not validation_result['is_valid']:
            print("Errors:")
            for error in validation_result['errors']:
                print(f"- {error}")
                
        print("\nGathering vendor information...")
        scraping_agent = ScrapingAgent()
        vendor_info = scraping_agent.scrape_vendor_info(invoice.vendor_name)
        
        print("\nVendor Information:")
        print(f"Company: {vendor_info['company']}")
        print(f"Description: {vendor_info['description']}")
        print(f"Website: {vendor_info['website']}")
        if vendor_info['social_links']:
            print("\nSocial Media Links:")
            for link in vendor_info['social_links']:
                print(f"- {link}")
                
    except Exception as e:
        print(f"\nError processing invoice: {str(e)}")
        print("\nDebug information:")
        print(f"Error type: {type(e).__name__}")
        print("Traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 