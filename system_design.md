# System Design

## Overview
The Invoice Processing Agent integrates Apify (scraping), Senso.ai (policy validation), and Gemini (data extraction) to automate high-volume invoice processing with enterprise security and auditability.

## Architecture
### Components:
1. **Apify Web Scraper**
   - Scrapes structured & unstructured invoices
   - Extracts key invoice fields (vendor, amount, due date)
   - Outputs JSON formatted data

2. **Gemini AI Processor**
   - Parses extracted invoice fields
   - Validates data consistency (e.g., matching totals)
   - Generates structured summaries for review

3. **Senso.ai Policy Validator**
   - Checks invoice terms against vendor policies
   - Flags violations (e.g., Net-30 violations)
   - Provides compliance explanations

4. **Audit & Logging Layer**
   - Logs data transformations at each stage
   - Stores policy validation reports
   - Ensures traceability for debugging

## Data Flow
1. Apify scrapes invoice data → JSON
2. Gemini processes fields → Validated output
3. Senso.ai checks policies → Policy-compliant report
4. CI/CD pipeline runs validations before merging

## Technology Stack
- **Scraping**: Apify (Node.js)
- **AI Processing**: Gemini (Python API)
- **Policy Validation**: Senso.ai API
- **Storage**: PostgreSQL for structured logs
- **CI/CD**: GitHub Actions for automated testing

## Security Considerations
- Encrypt vendor PII fields (bank details, addresses)
- Implement role-based access control (RBAC)
- Maintain audit logs for compliance tracking

## Scalability Plan
- Use Apify scaling for high-volume scraping
- Optimize Gemini queries for faster response times
- Implement caching for frequent policy checks
