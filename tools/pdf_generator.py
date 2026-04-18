# tools/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import os
import re

def clean_text(text: str) -> str:
    """Remove asterisks and markdown formatting from text"""
    # Remove ** bold markers
    text = text.replace('**', '')
    # Remove * italic markers
    text = text.replace('*', '')
    # Remove # heading markers
    text = text.replace('# ', '').replace('#', '')
    return text

def generate_title_from_query(query: str) -> str:
    """Generate a professional title from the research query"""
    # Remove common words and clean up
    title = query.strip()
    
    # Capitalize first letter and clean up
    if title:
        title = title[0].upper() + title[1:].lower()
    
    # Add research report suffix if not already there
    if not title.lower().endswith('report'):
        title += " - Research Report"
    
    return title

def generate_filename_from_query(query: str) -> str:
    """
    Generate a clean, concise filename from the research query
    Removes stop words and keeps only meaningful keywords
    
    Args:
        query: The research query
    
    Returns:
        Clean filename suitable for use
    """
    # Common stop words to remove (English + Urdu transliterations)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'is', 'are', 'am', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'can', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'why',
        'when', 'where', 'how', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your',
        'yours', 'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them',
        'their', 'theirs', 'tell', 'let', 'give', 'make', 'get', 'go', 'know', 'think',
        'see', 'say', 'as', 'about', 'also', 'just', 'only', 'very', 'so', 'also',
        'tell', 'me', 'about', 'the', 'is'
    }
    
    # Convert to lowercase and split into words
    words = query.strip().lower().split()
    
    # Filter out stop words - keep only meaningful keywords
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # If no keywords remain, use first few words
    if not keywords:
        keywords = words[:3]
    
    # Join keywords with underscores
    filename = '_'.join(keywords)
    
    # Remove special characters, keep only alphanumeric, underscores, and hyphens
    filename = re.sub(r'[^a-z0-9_\-]', '', filename)
    
    # Remove consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    # Limit length to 50 characters to avoid overly long filenames
    if len(filename) > 50:
        filename = filename[:50].rstrip('_')
    
    # If filename is still empty, use default
    if not filename:
        filename = "research_report"
    
    return filename

def generate_research_pdf(report_content: str, query: str, output_filename: str = None) -> str:
    """
    Generate a professional PDF report from research data.
    
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
    
    # Generate filename from query if not provided
    if not output_filename:
        output_filename = generate_filename_from_query(query) + ".pdf"
    
    pdf_path = os.path.join(output_dir, output_filename)
    
    # Create PDF with better margins
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter, 
        topMargin=0.75*inch, 
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    # Define professional styles
    title_style = ParagraphStyle(
        'DocumentTitle',
        parent=getSampleStyleSheet()['Heading1'],
        fontSize=26,
        textColor='#003366',
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=12,
        textColor='#666666',
        spaceAfter=18,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=getSampleStyleSheet()['Heading2'],
        fontSize=13,
        textColor='#FFFFFF',
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        leading=16
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    emphasis_style = ParagraphStyle(
        'Emphasis',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=10,
        leading=13,
        spaceAfter=6,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Build PDF content
    content = []
    
    # Generate automatic title from query
    auto_title = generate_title_from_query(query)
    content.append(Paragraph(auto_title, title_style))
    content.append(Spacer(1, 0.1*inch))
    
    # Metadata
    metadata_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}"
    content.append(Paragraph(metadata_text, subtitle_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Separator line
    separator = Table([['']], colWidths=[7.5*inch])
    separator.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#003366')),
    ]))
    content.append(separator)
    content.append(Spacer(1, 0.2*inch))
    
    # Parse and format the report content
    lines = report_content.split('\n')
    
    for i, line in enumerate(lines):
        original_line = line
        line = line.strip()
        
        # Skip empty lines, but add spacer
        if not line:
            content.append(Spacer(1, 0.08*inch))
            continue
        
        # Clean asterisks and special characters
        line = clean_text(line)
        
        # Identify section headers (uppercase with colon or just uppercase phrases)
        if (line.isupper() and ':' in line) or (line.isupper() and len(line) > 3):
            # Create header with colored background
            header_table = Table([[Paragraph(line, section_heading_style)]], colWidths=[7.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#003366')),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            content.append(header_table)
            content.append(Spacer(1, 0.08*inch))
        # Bullet points
        elif line.startswith('•') or line.startswith('-'):
            cleaned = line.lstrip('•-').strip()
            content.append(Paragraph(f"• {cleaned}", bullet_style))
        # Numbered items
        elif line and line[0].isdigit() and '.' in line[:3]:
            content.append(Paragraph(line, bullet_style))
        # Lines with confidence scores - make them stand out
        elif 'confidence' in line.lower() or '%' in line:
            content.append(Paragraph(line, emphasis_style))
        # Regular paragraphs
        else:
            content.append(Paragraph(line, normal_style))
    
    # Build PDF
    doc.build(content)
    
    return {
        "path": pdf_path,
        "filename": output_filename
    }
