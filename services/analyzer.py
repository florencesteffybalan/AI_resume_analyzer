import os
import json
import google.generativeai as genai
from google.api_core import exceptions as api_exceptions

def analyze_resume(resume_text):
    """
    Analyzes the resume text using Gemini API and returns detailed structured JSON.
    Dynamically detects profession, industry, and experience level from resume content.
    No hardcoded profession assumptions are made.
    """
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key or api_key.strip() == "" or api_key.strip() == "your_api_key_here":
        raise ValueError(
            "API Key Missing or Invalid: Please ensure your GEMINI_API_KEY is correctly set in the .env file and the server is restarted."
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
You are an expert AI Resume Analyzer and a world-class Senior Recruiter.

STEP 1 – DETECT PROFESSION:
Carefully read the entire resume and identify the candidate's exact profession, industry,
job role, and experience level (Fresher / Mid-Level / Senior / Executive) purely from the
resume content — keywords, job titles, education degrees, certifications, skills, and
project descriptions. Do NOT assume any profession. Do NOT default to IT or software.

Examples of correct detection:
- Nursing degree + clinical placements → "Staff Nurse", Healthcare
- B.Ed + teaching experience → "School Teacher", Education
- CPA + financial statements → "Accountant", Finance & Banking
- AutoCAD + structural drawings → "Civil Engineer", Construction & Engineering
- Campaigning + SEO + social media → "Digital Marketing Executive", Marketing
- No work experience + student → use degree/projects to determine field, mark as Fresher

STEP 2 – ACT AS INDUSTRY RECRUITER:
After detection, evaluate the resume EXACTLY as a Senior Recruiter from that industry would.
Apply industry-specific ATS scoring, keyword matching, and skill evaluation.
Do NOT apply software engineering standards to non-IT professions.

STEP 3 – PERSONALIZED ADVICE:
Every recommendation must be:
  a) Specific to the detected profession and industry
  b) Accompanied by a clear explanation of WHY it matters for that field
  c) Actionable and practical

If experience_level is Fresher or Student, focus advice on: internships, volunteer work,
foundational certifications, and projects relevant to that specific field.

OUTPUT FORMAT:
Return ONLY a valid raw JSON object with exactly these keys (no markdown, no code blocks):

{{
  "detected_profession": "Exact job title detected from the resume (e.g. Staff Nurse, Civil Engineer, School Teacher)",
  "industry": "Industry name (e.g. Healthcare, Education, Construction)",
  "experience_level": "Fresher | Mid-Level | Senior | Executive",
  "ats_score": <integer 0-100 based on this specific profession's ATS standards>,
  "category_scores": {{
    "formatting": <0-100>,
    "skills": <0-100>,
    "experience": <0-100>,
    "education": <0-100>,
    "keyword_optimization": <0-100>
  }},
  "contact_info": {{ "email": "...", "phone": "...", "linkedin": "..." }},
  "technical_skills": ["list", "of", "hard", "skills", "found"],
  "soft_skills": ["list", "of", "soft", "skills"],
  "education": [{{"degree": "...", "institution": "...", "year": "..."}}],
  "experience": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "duration": "Duration",
      "responsibilities": ["bullet 1", "bullet 2"]
    }}
  ],
  "projects": [{{"name": "...", "description": "..."}}],
  "certifications": ["list"],
  "achievements": ["list of notable wins"],
  "missing_skills": [
    {{"skill": "Skill Name", "explanation": "Why this skill is critical for this profession."}}
  ],
  "missing_keywords": [
    {{"keyword": "Keyword", "explanation": "Why ATS systems in this industry look for this term."}}
  ],
  "weak_sections": [
    {{"section": "Section Name", "explanation": "What is weak and why it matters."}}
  ],
  "content_improvements": [
    {{"suggestion": "Specific action", "explanation": "Why this change will strengthen the resume."}}
  ],
  "formatting_improvements": [
    {{"suggestion": "Formatting tip", "explanation": "Why this format is expected in this field."}}
  ],
  "career_growth_suggestions": [
    {{"suggestion": "Next step or certification", "explanation": "How this will advance their career in this field."}}
  ],
  "ats_optimization": [
    {{"suggestion": "ATS tip", "explanation": "How this improves ATS pass rate for this industry."}}
  ],
  "ai_solutions": {{
    "improved_summary": "A rewritten, powerful professional summary tailored to their profession and industry.",
    "improved_achievements": [
      "Rewritten bullet point 1 with quantifiable impact",
      "Rewritten bullet point 2 with quantifiable impact",
      "Rewritten bullet point 3 with quantifiable impact"
    ],
    "skills_presentation_advice": "How to best organise and present skills for this specific profession and industry."
  }}
}}

Resume Text:
{resume_text}
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
    except api_exceptions.InvalidArgument as e:
        raise ValueError(f"Invalid API Key or Model: The API key is invalid or the model 'gemini-2.5-flash' is unsupported. Details: {str(e)}")
    except api_exceptions.ResourceExhausted as e:
        raise ValueError("Rate Limit Exceeded: You have exceeded your Gemini API rate limits. Please wait a moment and try again.")
    except (api_exceptions.ServiceUnavailable, api_exceptions.RetryError) as e:
        raise ValueError("Service Unavailable: The Gemini API is currently unreachable. Please check your network connection or try again later.")
    except Exception as e:
        raise ValueError(f"Gemini API Error: An unexpected error occurred while communicating with the API: {str(e)}")

    # Strip any accidental markdown fences
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    try:
        result = json.loads(response_text.strip())
        return result
    except json.JSONDecodeError:
        print("=== RAW AI RESPONSE (JSON parse failed) ===")
        print(response_text)
        print("===========================================")
        raise ValueError(
            "The AI returned an unexpected format. "
            "Please try again or upload a cleaner resume file."
        )
