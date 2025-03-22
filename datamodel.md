# Data Model

## Invoice
- **invoice_id**: *UUID* - Unique identifier for the invoice.
- **vendor_id**: *UUID* - Identifier for the vendor.
- **invoice_number**: *String* - Invoice number as provided by the vendor.
- **invoice_date**: *Date* - Date the invoice was issued.
- **due_date**: *Date* - Payment due date.
- **total_amount**: *Decimal* - Total amount due.

## Vendor
- **vendor_id**: *UUID* - Unique identifier for the vendor.
- **vendor_name**: *String* - Name of the vendor.
- **vendor_address**: *String* - Address of the vendor.
- **contact_email**: *String* - Contact email for the vendor.

## PolicyValidation
- **validation_id**: *UUID* - Unique identifier for the validation record.
- **invoice_id**: 
