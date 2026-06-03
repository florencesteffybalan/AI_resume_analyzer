import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(data, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2563eb'), spaceAfter=10)
    subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontSize=14, textColor=colors.HexColor('#64748b'), spaceAfter=20)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#1e293b'), spaceBefore=15, spaceAfter=10)
    normal_style = styles['Normal']
    
    elements = []
    
    # Title & Profession Profile
    elements.append(Paragraph("AI Resume Analysis Report", title_style))
    
    profession = data.get("detected_profession", "Unknown")
    industry = data.get("industry", "Unknown")
    exp_level = data.get("experience_level", "Unknown")
    profile_text = f"<b>Profile:</b> {profession} | {industry} | {exp_level}"
    elements.append(Paragraph(profile_text, subtitle_style))
    
    # Overall Score
    ats_score = data.get("ats_score", 0)
    elements.append(Paragraph(f"<b>Overall ATS Score:</b> {ats_score}/100", normal_style))
    elements.append(Spacer(1, 10))
    
    # Category Scores
    elements.append(Paragraph("Category Breakdown", heading_style))
    scores = data.get("category_scores", {})
    score_data = [["Category", "Score"]]
    for cat, score in scores.items():
        score_data.append([cat.replace('_', ' ').title(), f"{score}/100"])
        
    if len(score_data) > 1:
        t = Table(score_data, colWidths=[200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1'))
        ]))
        elements.append(t)
    
    elements.append(Spacer(1, 15))
    
    # Recommendations
    elements.append(Paragraph("Detailed Recommendations", heading_style))
    
    def add_complex_list(title, items, key_name, explain_name):
        if items:
            elements.append(Paragraph(f"<b>{title}:</b>", normal_style))
            for item in items:
                k = item.get(key_name, "")
                exp = item.get(explain_name, "")
                elements.append(Paragraph(f"• <b>{k}</b>: {exp}", normal_style))
            elements.append(Spacer(1, 10))
            
    add_complex_list("Missing Industry Skills", data.get("missing_skills", []), "skill", "explanation")
    add_complex_list("Missing Keywords", data.get("missing_keywords", []), "keyword", "explanation")
    add_complex_list("Weak Sections", data.get("weak_sections", []), "section", "explanation")
    add_complex_list("Career Growth", data.get("career_growth_suggestions", []), "suggestion", "explanation")
    
    # AI Solutions
    elements.append(Paragraph("AI Generated Solutions", heading_style))
    ai_sol = data.get("ai_solutions", {})
    
    if ai_sol.get("improved_summary"):
        elements.append(Paragraph("<b>Improved Professional Summary:</b>", normal_style))
        elements.append(Paragraph(ai_sol["improved_summary"], normal_style))
        elements.append(Spacer(1, 10))
        
    if ai_sol.get("improved_achievements"):
        elements.append(Paragraph("<b>Stronger Achievements:</b>", normal_style))
        for ach in ai_sol["improved_achievements"]:
            elements.append(Paragraph(f"• {ach}", normal_style))
        elements.append(Spacer(1, 10))
        
    if ai_sol.get("skills_presentation_advice"):
        elements.append(Paragraph("<b>Skills Presentation Advice:</b>", normal_style))
        elements.append(Paragraph(ai_sol["skills_presentation_advice"], normal_style))
    
    doc.build(elements)
    return output_path
