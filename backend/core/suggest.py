import os, json, re
from typing import Dict, List

def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        pass
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I | re.M)
    m = re.search(r"\{.*\}", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {}

def _sanitize_list(val, max_len: int) -> List[str]:
    if not isinstance(val, list):
        return []
    out = []
    for x in val:
        if isinstance(x, str):
            s = x.strip()
            if s:
                out.append(s)
        if len(out) >= max_len:
            break
    return out

def generate_suggestions(resume_text: str, jd_text: str, missing_skills: List[str]) -> Dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"strengths": [], "suggestions": [], "cover_letter": ""}

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    model = os.getenv("SUGGESTIONS_MODEL", "gpt-4o-mini")

    # Tunable length for the cover letter
    min_words = int(os.getenv("COVER_LETTER_MIN_WORDS", "180"))
    max_words = int(os.getenv("COVER_LETTER_MAX_WORDS", "260"))

    system = (
        "You are a precise career coach for software roles. "
        "Only use information present in the provided resume and job description. "
        "Return ONE valid JSON object and nothing else. "
        'JSON schema: {"strengths": string[], "suggestions": string[], "cover_letter": string}. '
        "Constraints:\n"
        "• strengths: up to 4 short bullets grounded strictly in the resume that align to the JD; \n"
        "• suggestions: up to 4 concrete, resume-ready bullets the user can add NOW, each starting with a strong verb, "
        "naming specific techs/scope/impact (numbers if available). No courses/certifications/generic learning plans. "
        "Do not invent skills or experience not in the resume. If the JD lists skills missing from the resume, "
        "suggest alignment actions only if the resume shows evidence; otherwise omit.\n"
        f"• cover_letter: {min_words}-{max_words} words, 2–3 short paragraphs, include a greeting "
        "(e.g., 'Dear Hiring Manager,'), a concise closer ('Sincerely,'), and a placeholder name if none is provided. "
        "Use the job title and company only if explicitly present in the JD; otherwise say 'this role' and avoid naming. "
        "Ground claims in resume facts (techs, scope, quantified impact) that match JD needs. "
        "No apologies or filler; no extra keys; no code fences."
    )

    user = (
        f'Resume:\n""" {resume_text} """\n\n'
        f'Job Description:\n""" {jd_text} """\n\n'
        f"JD Missing skills (for context): {', '.join(missing_skills) if missing_skills else 'none'}\n"
    )

    resp = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        max_tokens=900,  # allow room for a full letter + lists
    )

    text = (resp.choices[0].message.content or "").strip()
    data = _extract_json(text)

    strengths = _sanitize_list(data.get("strengths", []), 4)
    suggestions = _sanitize_list(data.get("suggestions", []), 4)
    cover_letter = data.get("cover_letter", "")
    if not isinstance(cover_letter, str):
        cover_letter = ""

    return {
        "strengths": strengths,
        "suggestions": suggestions,
        "cover_letter": cover_letter.strip()
    }
