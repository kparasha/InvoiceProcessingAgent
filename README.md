# Invoice Processing Agent

A sophisticated multi-agent system for automated invoice processing, validation, and vendor management using AI.

## Overview

The Invoice Processing Agent is an intelligent system that combines multiple specialized AI agents to automate the invoice processing workflow. It uses OpenAI's GPT models for text extraction and analysis, computer vision for document processing, and implements a multi-agent architecture for distributed task handling.

## Features

- **PDF Invoice Processing**
  - Automated text and data extraction
  - Document metadata analysis
  - Multi-page support
  - Image and table extraction

- **Intelligent Data Extraction**
  - Company/vendor information detection
  - Invoice details (numbers, dates, amounts)
  - Line item parsing
  - Tax and total calculations

- **Validation & Verification**
  - Automated data validation
  - Mathematical accuracy checks
  - Cross-reference with historical data
  - Anomaly detection

- **Multi-Agent System**
  - ExtractionAgent: Handles document parsing and data extraction
  - ScrapingAgent: Validates vendor information
  - ComparisonAgent: Analyzes and compares invoice data
  - ValidationAgent: Ensures data accuracy and completeness

## Tech Stack

- **Backend**
  - FastAPI
  - Python 3.11+
  - OpenAI GPT-4
  - PyPDF2 for PDF processing
  - Pydantic for data validation

- **Frontend**
  - HTML5/CSS3
  - JavaScript
  - Responsive design
  - Real-time updates

- **Infrastructure**
  - Docker support
  - Render deployment
  - Environment-based configuration
  - Logging and monitoring

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/InvoiceProcessingAgent.git
cd InvoiceProcessingAgent
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your API keys and configuration
```

5. Start the server:
```bash
cd src
uvicorn app:app --reload
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `APIFY_API_KEY`: Your Apify API key
- `DEBUG`: Enable/disable debug mode
- `LOG_LEVEL`: Logging level configuration

## API Endpoints

- `POST /upload`: Upload and process invoice
- `GET /status/{job_id}`: Check processing status
- `GET /results/{job_id}`: Get processing results
- `POST /validate`: Validate extracted data

## Project Structure
