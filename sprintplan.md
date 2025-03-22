# Sprint Plan

## Sprint Goal
Automate invoice processing by integrating Apify (scraping), Senso.ai (policy validation), and Gemini (data extraction) within a structured CI/CD pipeline.

## Sprint Duration
**2 hours** (Broken into 30-minute pair programming slots)

## Sprint Backlog
### Tasks & Pair Programming Slots

1. **Invoice Scraping Setup (Apify)** (30 min)
   - Define Apify crawlers for structured and unstructured invoices
   - Store extracted data in JSON format
   - Validate data against sample invoices

2. **Invoice Field Extraction (Gemini AI)** (30 min)
   - Design Gemini prompts for key invoice fields (date, amount, vendor)
   - Implement Gemini validation logic
   - Write unit tests for field extraction

3. **Policy Validation (Senso.ai)** (30 min)
   - Retrieve policy rules from Senso.ai API
   - Implement validation logic for invoice terms
   - Test policy violations using sample invoices

4. **End-to-End Integration** (30 min)
   - Connect Apify → Gemini → Senso.ai into a single pipeline
   - Mock end-to-end invoice processing
   - Debug any issues in data flow

5. **Testing & CI/CD Integration** (30 min)
   - Automate tests using mocked invoice PDFs
   - Implement GitHub Actions for automated validation
   - Set up logging for audit trails

6. **Final Review & Deployment** (30 min)
   - Code review and refactoring
   - Deploy test environment
   - Generate sample reports for validation

## Sprint Success Metrics
- Successfully extracted invoice data from 5+ formats
- Validated invoice terms against Senso.ai policies
- Automated processing with at least 90% accuracy
- Established CI/CD pipeline for future enhancements
