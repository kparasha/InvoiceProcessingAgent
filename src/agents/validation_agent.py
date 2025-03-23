from datetime import datetime
from typing import Dict, List, Union
from src.utils.models import Invoice
from src.utils.logger import logger

class ValidationAgent:
    """Agent responsible for validating invoice data against business rules"""
    
    def validate_invoice(self, invoice_data: Dict) -> Dict[str, Union[bool, List[str]]]:
        """
        Validate invoice data against business rules.
        
        Args:
            invoice_data: Dictionary containing invoice data
            
        Returns:
            Dict containing validation results with keys:
            - is_valid: bool indicating if all validations passed
            - errors: list of error messages if any validations failed
        """
        errors = []
        logger.info(f"Starting validation for invoice {invoice_data.get('invoice_number', 'UNKNOWN')}")
        
        # Required fields
        if not invoice_data.get('invoice_number'):
            errors.append("Invoice number is required")
            logger.warning("Missing invoice number")
        
        if not invoice_data.get('vendor_name'):
            errors.append("Vendor name is required")
            logger.warning("Missing vendor name")
            
        if not invoice_data.get('date'):
            errors.append("Invoice date is required")
            logger.warning("Missing invoice date")
            
        if not invoice_data.get('total_amount'):
            errors.append("Total amount is required")
            logger.warning("Missing total amount")
            
        # Line items validation
        line_items = invoice_data.get('line_items', [])
        if not line_items:
            errors.append("At least one line item is required")
            logger.warning("No line items found")
        else:
            total = sum(float(item.get('amount', 0)) for item in line_items)
            stated_total = float(invoice_data.get('total_amount', 0))
            if abs(total - stated_total) > 0.01:  # Allow for small floating point differences
                errors.append(f"Line items total ({total}) does not match invoice total ({stated_total})")
                logger.warning(f"Total amount mismatch: line items {total} vs stated {stated_total}")

        # Date validations
        try:
            invoice_date = datetime.strptime(invoice_data.get('date', ''), '%Y-%m-%d')
            if invoice_date > datetime.now():
                errors.append("Invoice date cannot be in the future")
                logger.warning("Future invoice date detected")
                
            if invoice_data.get('due_date'):
                due_date = datetime.strptime(invoice_data['due_date'], '%Y-%m-%d')
                if due_date < invoice_date:
                    errors.append("Due date cannot be before invoice date")
                    logger.warning("Due date before invoice date")
        except ValueError as e:
            errors.append(f"Invalid date format: {str(e)}")
            logger.warning(f"Date format error: {str(e)}")

        is_valid = len(errors) == 0
        logger.info(f"Validation completed. Valid: {is_valid}")
        if not is_valid:
            logger.warning(f"Validation errors: {errors}")
            
        return {
            "is_valid": is_valid,
            "errors": errors
        } 