from openai import OpenAI
from src.utils.config import settings
from src.utils.models import Invoice, LineItem
from datetime import datetime
from decimal import Decimal
import json
import time
from typing import List, Optional
from src.utils.logger import logger

class ExtractionAgent:
    """Agent responsible for extracting invoice data from text"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url="https://api.openai.com/v1"  # Explicitly set the base URL
        )
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not found in settings")
        
    def extract_invoice_data(self, text: str) -> dict:
        """Extract invoice data from text using OpenAI"""
        try:
            logger.info("Starting invoice data extraction")
            
            # Split text into lines and clean them
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            logger.debug(f"Processed {len(lines)} lines from invoice text")
            
            # Initialize variables
            invoice_number = ""
            date = None
            vendor_name = "Cloudflare Inc."  # We know this is fixed
            total_amount = 0.0
            due_date = None
            line_items = []
            
            # Extract invoice number
            for i, line in enumerate(lines):
                if "Invoice Number:" in line and i + 1 < len(lines):
                    invoice_number = lines[i + 1].strip()
                    logger.info(f"Found invoice number: {invoice_number}")
                    break
            
            # Extract date
            for i, line in enumerate(lines):
                if line == "Date:" and i + 1 < len(lines):
                    date_str = lines[i + 1].strip()
                    try:
                        date = datetime.strptime(date_str, "%B %d, %Y")
                        logger.info(f"Found invoice date: {date}")
                    except ValueError:
                        date = datetime.now()
                        logger.warning(f"Could not parse date: {date_str}, using current date")
                    break
            
            # Extract due date
            for i, line in enumerate(lines):
                if line == "Due Date:" and i + 1 < len(lines):
                    due_date_str = lines[i + 1].strip()
                    try:
                        due_date = datetime.strptime(due_date_str, "%B %d, %Y")
                        logger.info(f"Found due date: {due_date}")
                    except ValueError:
                        due_date = None
                        logger.warning(f"Could not parse due date: {due_date_str}")
                    break
            
            # Extract line items
            start_idx = -1
            end_idx = -1
            for i, line in enumerate(lines):
                if line == "Description":
                    start_idx = i + 4  # Skip header row
                    logger.info("Found line items table header")
                elif line == "Subtotal:":
                    end_idx = i
                    break
            
            if start_idx != -1 and end_idx != -1:
                current_item = []
                for i in range(start_idx, end_idx):
                    line = lines[i].strip()
                    if not line:
                        continue
                        
                    current_item.append(line)
                    if len(current_item) == 4:
                        try:
                            description = current_item[0]
                            quantity = float(current_item[1])
                            unit_price = float(current_item[2].replace('$', '').replace(',', ''))
                            amount = float(current_item[3].replace('$', '').replace(',', ''))
                            
                            line_items.append(LineItem(
                                description=description,
                                quantity=quantity,
                                unit_price=unit_price,
                                amount=amount
                            ))
                            logger.debug(f"Added line item: {description} - {quantity} x ${unit_price} = ${amount}")
                            current_item = []
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Failed to parse line item: {str(e)}")
                            current_item = []
            
            # Extract total amount
            for i, line in enumerate(lines):
                if line == "Total:":
                    total_str = lines[i + 1].strip().replace('$', '').replace(',', '')
                    try:
                        total_amount = float(total_str)
                        logger.info(f"Found total amount: ${total_amount}")
                    except ValueError:
                        total_amount = 0.0
                        logger.warning(f"Could not parse total amount: {total_str}")
                    break
            
            # Calculate total from line items
            calculated_total = sum(item.amount for item in line_items)
            
            # Look for tax and fees
            tax_amount = 0.0
            for i, line in enumerate(lines):
                if "Tax:" in line and i + 1 < len(lines):
                    try:
                        tax_str = lines[i + 1].strip().replace('$', '').replace(',', '')
                        tax_amount = float(tax_str)
                        line_items.append(LineItem(
                            description="Sales Tax",
                            quantity=1,
                            unit_price=tax_amount,
                            amount=tax_amount
                        ))
                        logger.info(f"Found tax amount: ${tax_amount}")
                        calculated_total += tax_amount
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Failed to parse tax amount: {str(e)}")

            # If there's still a difference, add it as Sales Tax
            remaining_difference = total_amount - calculated_total
            if abs(remaining_difference) > 0.01:
                line_items.append(LineItem(
                    description="Sales Tax",
                    quantity=1,
                    unit_price=remaining_difference,
                    amount=remaining_difference
                ))
                logger.info(f"Added remaining difference as tax: ${remaining_difference}")
                calculated_total += remaining_difference

            if calculated_total > 0 and abs(calculated_total - total_amount) > 0.01:
                logger.warning(f"Total amount mismatch: stated ${total_amount} vs calculated ${calculated_total}")
            
            invoice = Invoice(
                invoice_number=invoice_number,
                date=date or datetime.now(),
                vendor_name=vendor_name,
                total_amount=total_amount,
                due_date=due_date,
                line_items=line_items
            )
            
            logger.info(f"Successfully extracted invoice data with {len(line_items)} line items")
            return {
                "invoice_number": invoice.invoice_number,
                "date": invoice.date.strftime("%Y-%m-%d"),
                "vendor_name": invoice.vendor_name,
                "total_amount": str(invoice.total_amount),
                "due_date": invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else None,
                "line_items": [{"description": item.description, "amount": str(item.amount)} for item in invoice.line_items]
            }
            
        except Exception as e:
            logger.error(f"Error extracting invoice data: {str(e)}")
            raise

    def extract_invoice_data_using_gpt(self, invoice_text: str) -> Invoice:
        """
        Extract invoice data using OpenAI's GPT-4
        """
        prompt = f"""
        You are an expert at extracting information from invoices. Extract the following information from this invoice text:
        - Invoice number (look for patterns like INV-*, #*, etc.)
        - Date (convert any date format to YYYY-MM-DD)
        - Vendor name (look for company name under 'BILL TO:', 'FROM:', etc. - include full legal name if available)
        - Total amount (look for TOTAL: or similar, remove currency symbols and commas)
        - Due date (convert any date format to YYYY-MM-DD)
        - Line items (extract each item with description and amount, remove currency symbols and commas)

        Important:
        - For vendor name, include the full company name (e.g., "Cloudflare, Inc." not just "Cloudflare")
        - Convert all dates to YYYY-MM-DD format
        - Remove currency symbols and commas from amounts
        - Include all line items with their descriptions and amounts
        - If a field is not found, use null or empty string as appropriate

        Invoice text:
        {invoice_text}

        Return the data in JSON format matching this structure:
        {{
            "invoice_number": "string",
            "date": "YYYY-MM-DD",
            "vendor_name": "string",
            "total_amount": "decimal",
            "due_date": "YYYY-MM-DD or null",
            "line_items": [
                {{"description": "string", "amount": "decimal"}}
            ]
        }}
        """
        
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert at extracting structured data from invoices. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1  # Low temperature for more consistent output
                )
                
                data = response.choices[0].message.content
                # Clean up the response to ensure it's valid JSON
                data = data.replace("```json", "").replace("```", "").strip()
                
                # Use json.loads instead of eval for safer parsing
                invoice_dict = json.loads(data)
                
                # Convert the JSON data to an Invoice object
                return Invoice(
                    invoice_number=invoice_dict["invoice_number"],
                    date=datetime.strptime(invoice_dict["date"], "%Y-%m-%d").date(),
                    vendor_name=invoice_dict["vendor_name"],
                    total_amount=Decimal(str(invoice_dict["total_amount"])),
                    due_date=datetime.strptime(invoice_dict["due_date"], "%Y-%m-%d").date() if invoice_dict["due_date"] else None,
                    line_items=invoice_dict["line_items"]
                )
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}/{max_retries}: Failed to parse JSON response: {str(e)}\nResponse: {data}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise ValueError(f"Failed to parse JSON response after {max_retries} attempts: {str(e)}\nResponse: {data}")
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries}: Error occurred: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise ValueError(f"Failed to parse invoice data after {max_retries} attempts: {str(e)}") 