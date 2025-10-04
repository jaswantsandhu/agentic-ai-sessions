"""
Simple PDF creator using fpdf2
"""
try:
    from fpdf import FPDF
except ImportError:
    print("Installing fpdf2...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fpdf2', '--break-system-packages'])
    from fpdf import FPDF

import os

def create_nda_pdf():
    """Create NDA PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    # Read content
    with open('sample_nda.txt', 'r') as f:
        content = f.read()

    # Title
    pdf.cell(0, 10, 'NON-DISCLOSURE AGREEMENT', 0, 1, 'C')
    pdf.ln(5)

    # Content
    pdf.set_font("Arial", size=10)

    # Process content
    for line in content.split('\n'):
        if line.strip():
            if line.strip().isupper() and len(line.strip()) < 50 and not line.startswith(' '):
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 6, line.strip())
                pdf.set_font("Arial", size=10)
            else:
                pdf.multi_cell(0, 5, line.strip())
        else:
            pdf.ln(3)

    # Save
    os.makedirs('sample_documents', exist_ok=True)
    pdf.output('sample_documents/sample_nda.pdf')
    print("✅ Created: sample_documents/sample_nda.pdf")

def create_service_agreement_pdf():
    """Create Service Agreement PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    content = """SERVICE AGREEMENT

This Service Agreement is entered into as of February 1, 2024, between WebDev Solutions Inc. ("Service Provider") and Global Retail Corp. ("Client").

1. SERVICES

Service Provider agrees to provide web development and maintenance services including:
- Custom e-commerce platform development
- Monthly website maintenance and updates
- Security monitoring and patches
- 24/7 technical support

2. TERM

This Agreement shall commence on February 1, 2024 and continue for an initial term of twelve (12) months. The Agreement will automatically renew for successive one-year terms unless either party provides written notice of termination at least sixty (60) days prior to the end of the then-current term.

3. PAYMENT TERMS

Client agrees to pay Service Provider as follows:
- Initial development fee: $50,000 (due upon signing)
- Monthly maintenance fee: $5,000 (due on the 1st of each month)
- Additional services billed at $150 per hour

Payment is due within thirty (30) days of invoice date. Late payments will incur a 1.5% monthly interest charge.

4. TERMINATION

Either party may terminate this Agreement:
a) For convenience with sixty (60) days written notice
b) Immediately for material breach if not cured within thirty (30) days of written notice
c) Immediately if the other party becomes insolvent or files for bankruptcy

Upon termination, Client shall pay for all services performed through the termination date plus any outstanding invoices.

5. INTELLECTUAL PROPERTY

All custom code and designs created specifically for Client shall become Client's property upon full payment. Service Provider retains ownership of any pre-existing code, frameworks, or tools used in providing services.

6. WARRANTIES

Service Provider warrants that services will be performed in a professional and workmanlike manner consistent with industry standards. Client's exclusive remedy for breach of warranty is re-performance of deficient services at no additional cost.

7. LIMITATION OF LIABILITY

Service Provider's total liability under this Agreement shall not exceed the total fees paid by Client in the twelve (12) months preceding the claim. Service Provider is not liable for indirect, incidental, consequential, or punitive damages.

8. CONFIDENTIALITY

Both parties agree to maintain confidentiality of proprietary information disclosed during the term of this Agreement and for two (2) years thereafter.

9. GOVERNING LAW

This Agreement is governed by the laws of the State of New York without regard to conflict of law principles.

10. ENTIRE AGREEMENT

This Agreement constitutes the entire agreement between the parties and supersedes all prior agreements, whether written or oral.

EXECUTED as of the date first written above.

SERVICE PROVIDER: WebDev Solutions Inc.
By: Robert Martinez, CEO
Date: February 1, 2024

CLIENT: Global Retail Corp.
By: Jennifer Williams, CTO
Date: February 1, 2024"""

    # Title
    pdf.cell(0, 10, 'SERVICE AGREEMENT', 0, 1, 'C')
    pdf.ln(5)

    # Content
    pdf.set_font("Arial", size=10)

    for line in content.split('\n'):
        if line.strip():
            if line.strip().isupper() and len(line.strip()) < 50 and not line.startswith(' '):
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 6, line.strip())
                pdf.set_font("Arial", size=10)
            elif line.strip().startswith(tuple('123456789')):
                pdf.set_font("Arial", 'B', 11)
                pdf.multi_cell(0, 6, line.strip())
                pdf.set_font("Arial", size=10)
            else:
                pdf.multi_cell(0, 5, line.strip())
        else:
            pdf.ln(2)

    pdf.output('sample_documents/sample_service_agreement.pdf')
    print("✅ Created: sample_documents/sample_service_agreement.pdf")

if __name__ == "__main__":
    try:
        create_nda_pdf()
        create_service_agreement_pdf()
        print("\n✅ All sample PDF documents created successfully!")
        print("\nYou can now test the application with these documents.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
