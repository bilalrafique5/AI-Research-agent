# tools/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
import os

def generate_research_pdf(report_content: str, query: str, output_filename: str = None) -> str:
    """
    Generate a PDF report from research data.
    
    Args:
        report_content: The formatted report text
        query: The original research query
        output_filename: Optional custom filename
    
    Returns:
        Path to the generated PDF file
    """
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"research_report_{timestamp}.pdf"
    
    pdf_path = os.path.join(output_dir, output_filename)
    
    # Create PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f4788',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2E5090',
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=6
    )
    
    # Build PDF content
    content = []
    
    # Title
    content.append(Paragraph("Research Report", title_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Query/Topic
    content.append(Paragraph(f"<b>Query:</b> {query}", normal_style))
    content.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    content.append(Spacer(1, 0.3*inch))
    
    # Parse and format the report content
    lines = report_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            content.append(Spacer(1, 0.1*inch))
            continue
        
        # Check if it's a section header (all caps with colon)
        if line.isupper() and ':' in line:
            content.append(Paragraph(line, heading_style))
            content.append(Spacer(1, 0.1*inch))
        # Check if it's a bullet point
        elif line.startswith('•') or line.startswith('-'):
            content.append(Paragraph(line, normal_style))
        # Check if it's a numbered item
        elif line[0].isdigit() and '.' in line[:3]:
            content.append(Paragraph(line, normal_style))
        else:
            content.append(Paragraph(line, normal_style))
    
    # Build PDF
    doc.build(content)
    
    return pdf_path
