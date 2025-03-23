# Data Model Documentation

## Core Data Structures

### Invoice Data
```python
class Invoice:
    id: str
    vendor_info: VendorInfo
    invoice_details: InvoiceDetails
    line_items: List[LineItem]
    totals: InvoiceTotals
    metadata: DocumentMetadata
```

### Vendor Information
```python
class VendorInfo:
    name: str
    tax_id: Optional[str]
    address: str
    contact: Optional[ContactInfo]
```

### Invoice Details
```python
class InvoiceDetails:
    invoice_number: str
    date: datetime
    due_date: Optional[datetime]
    terms: Optional[str]
    po_number: Optional[str]
```

### Line Items
```python
class LineItem:
    description: str
    quantity: float
    unit_price: float
    amount: float
    tax: Optional[float]
```

### Document Metadata
```python
class DocumentMetadata:
    file_name: str
    file_size: int
    page_count: int
    creation_date: datetime
    modification_date: datetime
```

## Validation Models

### Validation Result
```python
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
```

### Processing Status
```python
class ProcessingStatus:
    job_id: str
    status: StatusEnum
    progress: float
    message: str
    timestamp: datetime
```
