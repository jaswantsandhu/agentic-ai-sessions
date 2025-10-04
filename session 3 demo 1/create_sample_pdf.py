"""
Script to create sample PDF legal documents for testing
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_nda_pdf():
    """Create NDA PDF from text file"""
    # Read the NDA text
    with open('sample_nda.txt', 'r') as f:
        content = f.read()

    # Create PDF
    pdf_file = 'sample_documents/sample_nda.pdf'
    doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    # Container for elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='black',
        spaceAfter=30,
        alignment=1  # Center
    )

    # Split content into paragraphs
    paragraphs = content.split('\n\n')

    for para in paragraphs:
        if para.strip():
            if para.strip().isupper() and len(para.strip()) < 50:
                # It's a heading
                elements.append(Paragraph(para.strip(), title_style))
            else:
                # Regular paragraph
                elements.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))

    # Build PDF
    doc.build(elements)
    print(f"Created: {pdf_file}")

def create_service_agreement_pdf():
    """Create a sample service agreement PDF"""
    pdf_file = 'sample_documents/sample_service_agreement.pdf'
    doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    elements = []
    styles = getSampleStyleSheet()

    content = """
SERVICE AGREEMENT

This Service Agreement is entered into as of February 1, 2024, between WebDev Solutions Inc. ("Service Provider")
and Global Retail Corp. ("Client").

1. SERVICES
Service Provider agrees to provide web development and maintenance services including:
- Custom e-commerce platform development
- Monthly website maintenance and updates
- Security monitoring and patches
- 24/7 technical support

2. TERM
This Agreement shall commence on February 1, 2024 and continue for an initial term of twelve (12) months.
The Agreement will automatically renew for successive one-year terms unless either party provides written
notice of termination at least sixty (60) days prior to the end of the then-current term.

3. PAYMENT TERMS
Client agrees to pay Service Provider as follows:
- Initial development fee: $50,000 (due upon signing)
- Monthly maintenance fee: $5,000 (due on the 1st of each month)
- Additional services billed at $150 per hour
Payment is due within thirty (30) days of invoice date.

4. TERMINATION
Either party may terminate this Agreement:
a) For convenience with sixty (60) days written notice
b) Immediately for material breach if not cured within thirty (30) days of written notice
c) Immediately if the other party becomes insolvent or files for bankruptcy

Upon termination, Client shall pay for all services performed through the termination date.

5. INTELLECTUAL PROPERTY
All custom code and designs created specifically for Client shall become Client's property upon full payment.
Service Provider retains ownership of any pre-existing code, frameworks, or tools used in providing services.

6. WARRANTIES
Service Provider warrants that services will be performed in a professional and workmanlike manner consistent
with industry standards. Client's exclusive remedy for breach of warranty is re-performance of deficient services.

7. LIMITATION OF LIABILITY
Service Provider's total liability shall not exceed the fees paid by Client in the twelve (12) months preceding
the claim. Service Provider is not liable for indirect, incidental, or consequential damages.

8. CONFIDENTIALITY
Both parties agree to maintain confidentiality of proprietary information disclosed during the term of this Agreement
and for two (2) years thereafter.

9. GOVERNING LAW
This Agreement is governed by the laws of the State of New York.

EXECUTED as of the date first written above.

Service Provider: WebDev Solutions Inc.
By: ________________________
Name: Robert Martinez
Title: CEO

Client: Global Retail Corp.
By: ________________________
Name: Jennifer Williams
Title: CTO
"""

    for para in content.split('\n\n'):
        if para.strip():
            elements.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    print(f"Created: {pdf_file}")

if __name__ == "__main__":
    try:
        create_nda_pdf()
        create_service_agreement_pdf()
        print("\n✅ Sample PDF documents created successfully!")
    except ImportError:
        print("\n⚠️  reportlab not installed. Installing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'reportlab'])
        print("Please run this script again.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
