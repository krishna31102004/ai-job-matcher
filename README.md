Here’s a cleaned-up, recruiter-ready **README.md** you can paste into the repo root.

---

# AI Job Matcher — Starter

Minimal **FastAPI** backend + **React (Vite)** frontend.

* Upload a resume (**PDF/DOCX**) and paste a job description.
* Backend returns a **match score** (TF-IDF cosine + skills overlap) and a **skills diff**.
* Optional **LLM suggestions** (strengths, resume-ready bullets, cover letter) when `detailed=true` and an OpenAI key is set.
* Skills extractor is simple and easy to extend.

---

## Project Structure

```
ai-job-matcher-starter/
  backend/
    app.py                # FastAPI app (serves /api/*)
    core/
      parse.py            # PDF/DOCX → text
      match.py            # TF-IDF/embeddings + overlap scoring
      nlp.py              # skill extraction + synonyms
      embed.py            # switchable: tfidf | hf | openai
      suggest.py          # LLM suggestions (OpenAI)
    tests/
      test_match.py       # unit tests
    requirements.txt
  frontend/
    src/
      App.jsx             # upload + results UI
      main.jsx
    vite.config.js        # dev proxy /api → 8000
    package.json
  .env                    # environment variables (not committed)
  README.md
```

---

## Quickstart (Development)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app:app --reload
```

**API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend

```bash
cd frontend
npm i
npm run dev
```

**Dev server:** [http://localhost:5173](http://localhost:5173)  (Vite proxies `/api` → `http://localhost:8000`)

---

## Environment

Create a `.env` in the **repo root** (one is already generated). Edit as needed:

```ini
# Embeddings
EMBED_MODE=tfidf                    # tfidf (default) | hf | openai
EMBED_MODEL_HF=sentence-transformers/all-MiniLM-L6-v2
EMBED_MODEL_OPENAI=text-embedding-3-small

# LLM suggestions (used when detailed=true)
OPENAI_API_KEY=                     # set to enable suggestions and/or OpenAI embeddings
SUGGESTIONS_MODEL=gpt-4o-mini

# Server
PORT=8080
ALLOW_ORIGINS=*                     # tighten for production if exposing cross-origin
```

The backend auto-loads `.env` via `python-dotenv`.

---

## API

### 1) Text-only endpoint (no file)

```
POST /api/match_text
Content-Type: application/json
{
  "resume_text": "...",
  "job_description": "...",
  "detailed": true
}
```

**Response (example):**

```json
{
  "score": 82.4,
  "semantic_pct": 70.5,
  "overlap_pct": 90.0,
  "top_overlap_skills": ["python","docker","aws"],
  "missing_skills": ["sql"],
  "strengths": ["..."],
  "suggestions": ["..."],
  "cover_letter": "..."
}
```

### 2) File upload endpoint

* **Route:** `POST /api/match`
* **Form fields (multipart/form-data):**

  * `resume_file` = PDF or DOCX
  * `job_description` = string
  * `detailed` = `true|false`

---

## How Scoring Works (MVP)

* **Semantic:** TF-IDF cosine similarity (can switch to Sentence-Transformers or OpenAI embeddings).
* **Skills overlap:** intersection of JD vs resume skills (from `core/nlp.py`).
* **Final score:** `0.4 * semantic + 0.6 * overlap`.

> Tune weights in `backend/core/match.py`.
> Expand skills & synonyms in `backend/core/nlp.py` (see `TECH_SKILLS` & `ALIASES`).

---

## Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

---

## Notes

* The default semantic baseline is **TF-IDF**. You can switch to **Sentence-Transformers** (`EMBED_MODE=hf`) or **OpenAI embeddings** (`EMBED_MODE=openai`).
* LLM suggestions (strengths, resume-ready bullets, cover letter) require `OPENAI_API_KEY` and `detailed=true`.
* The curated skills list and synonym map live in `backend/core/nlp.py`. Add techs or aliases as you go.

---

## (Optional) Production

A Docker setup can build the React app and serve it via FastAPI at `/`, with the API under `/api/*`. See `Dockerfile` and `docker-compose.yml` if included in your repo.

---
