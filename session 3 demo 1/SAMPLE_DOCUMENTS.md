# Sample Legal Documents

## Creating Test PDFs

Since the automatic PDF creation script requires additional dependencies, you can create sample PDFs manually using one of these methods:

### Method 1: Use Online Text to PDF Converter

1. Copy the content from [sample_nda.txt](sample_nda.txt)
2. Visit any online text-to-PDF converter (e.g., [https://www.ilovepdf.com/txt_to_pdf](https://www.ilovepdf.com/txt_to_pdf))
3. Convert and save as `sample_documents/sample_nda.pdf`

### Method 2: Use Google Docs or Microsoft Word

1. Open [sample_nda.txt](sample_nda.txt) in a text editor
2. Copy the content
3. Paste into Google Docs or Microsoft Word
4. Save/Export as PDF to `sample_documents/`

### Method 3: Use Python Script (if you have a virtual environment)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install fpdf2
pip install fpdf2

# Run the PDF creator
python simple_pdf_creator.py
```

### Method 4: Use System Tools (macOS)

```bash
# Convert text to PDF using textutil and cupsfilter (macOS)
textutil -convert html sample_nda.txt -output sample_nda.html
cupsfilter sample_nda.html > sample_documents/sample_nda.pdf
```

## Available Sample Documents

### 1. Non-Disclosure Agreement (NDA)
**File**: `sample_nda.txt` → Convert to PDF

**Key Points**:
- Parties: TechCorp Industries Inc. and Digital Solutions LLC
- Purpose: Protecting confidential AI technology information
- Duration: 5 years for general information, indefinite for trade secrets
- Effective Date: January 15, 2024

**Test Questions**:
- "What is the duration of the confidentiality obligation?"
- "Who are the parties involved?"
- "What happens if there's a breach?"
- "What are the exceptions to confidentiality?"

### 2. Service Agreement
**Content available in**: `simple_pdf_creator.py` (extract the content string)

**Key Points**:
- Parties: WebDev Solutions Inc. and Global Retail Corp.
- Services: Web development and maintenance
- Term: 12 months with auto-renewal
- Payment: $50,000 initial + $5,000/month

**Test Questions**:
- "What are the terms for termination?"
- "What are the payment terms?"
- "What services are included?"
- "How long is the initial term?"

## Quick Start Without PDFs

If you want to test the application immediately without creating PDFs, you can:

1. Find any legal PDF document online:
   - [SEC EDGAR filings](https://www.sec.gov/edgar/searchedgar/companysearch.html) (public company agreements)
   - [Creative Commons license documents](https://creativecommons.org/licenses/)
   - Free legal templates from [LawDepot](https://www.lawdepot.com/) or similar sites

2. Download and use them for testing

3. Or create a simple PDF from any text editor by printing to PDF

## Notes

- Ensure PDFs are text-based (not scanned images)
- The application works best with well-structured legal documents
- For production use, always use real legal documents reviewed by professionals
