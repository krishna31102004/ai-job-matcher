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

    system = (
        "You are a concise career coach for software roles. "
        "Only use information present in the provided resume and job description. "
        "Output ONE valid JSON object and nothing else. "
        "JSON schema: {\"strengths\": string[], \"suggestions\": string[], \"cover_letter\": string}. "
        "Constraints: "
        "• strengths: up to 4 short bullets grounded strictly in the resume that align to the JD; "
        "• suggestions: up to 4 concrete, resume-ready bullets the user can add NOW, each starting with a strong verb, "
        "naming specific techs/scope/impact (numbers if available). "
        "Do NOT propose courses, certifications, generic learning plans, or open-source contributions. "
        "Do NOT invent skills or experience not present in the resume. "
        "If the JD lists skills missing from the resume, suggest alignment actions ONLY if the resume already shows evidence; "
        "otherwise omit that item from suggestions. "
        "Cover letter: 4–5 sentences, grounded only in resume facts and JD needs; do not claim skills not in the resume; "
        "no apologies, no filler."
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
        temperature=0.1,
        max_tokens=500,
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
