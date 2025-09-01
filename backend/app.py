import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os as _os

from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from core.parse import extract_text_from_upload
from core.match import compute_score
from core.nlp import extract_skills_simple, find_missing_skills_simple
from core.embed import get_embedder
try:
    from core.suggest import generate_suggestions
except Exception:
    def generate_suggestions(*args, **kwargs):
        return {"strengths": [], "suggestions": [], "cover_letter": ""}

load_dotenv(find_dotenv())
app = FastAPI(title="AI Job Matcher - Starter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_os.getenv("ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve built frontend (Vite) from /app/static
try:
    static_dir = Path(__file__).parent.parent / "static"
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
except Exception:
    pass

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    index_file = Path(__file__).parent.parent / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"status": "ok", "embed_mode": os.getenv("EMBED_MODE", "tfidf")}

@app.post("/api/match")
async def match(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    detailed: bool = Form(False)
):
    if resume_file.content_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or DOCX.")

    resume_text = await extract_text_from_upload(resume_file)
    jd_text = job_description

    embedder = get_embedder()
    score, semantic_pct, overlap_pct, top_overlap = compute_score(resume_text, jd_text, embedder)
    jd_skills = extract_skills_simple(jd_text)
    resume_skills = extract_skills_simple(resume_text)
    missing = find_missing_skills_simple(jd_skills, resume_skills)

    result = {
        "score": round(score, 1),
        "semantic_pct": round(semantic_pct, 1),
        "overlap_pct": round(overlap_pct, 1),
        "top_overlap_skills": top_overlap[:8],
        "missing_skills": missing[:10],
        "strengths": [],
        "suggestions": []
    }
    if detailed:
        rec = generate_suggestions(resume_text, jd_text, missing)
        result.update(rec)

    return JSONResponse(result)


class MatchTextIn(BaseModel):
    resume_text: str
    job_description: str
    detailed: bool = False

@app.post("/api/match_text")
async def match_text(payload: MatchTextIn):
    resume_text = payload.resume_text
    jd_text = payload.job_description
    embedder = get_embedder()
    score, semantic_pct, overlap_pct, top_overlap = compute_score(resume_text, jd_text, embedder)
    jd_skills = extract_skills_simple(jd_text)
    resume_skills = extract_skills_simple(resume_text)
    missing = find_missing_skills_simple(jd_skills, resume_skills)
    result = {
        "score": round(score, 1),
        "semantic_pct": round(semantic_pct, 1),
        "overlap_pct": round(overlap_pct, 1),
        "top_overlap_skills": top_overlap[:8],
        "missing_skills": missing[:10],
        "strengths": [],
        "suggestions": []
    }
    if payload.detailed:
        rec = generate_suggestions(resume_text, jd_text, missing)
        result.update(rec)
    return result
