# AI Job Matcher

Upload a **PDF/DOCX resume** and paste a **job description** to instantly get:

* a **match score** (semantic + skills overlap),
* **overlapping / missing skills**, and
* optional **LLM suggestions** (resume-ready bullets + cover letter).

**Live App:** [https://ai-job-matcher-beige.vercel.app](https://ai-job-matcher-beige.vercel.app)

**API Docs:** [https://ai-job-matcher-kw97.onrender.com/docs](https://ai-job-matcher-kw97.onrender.com/docs)

> Built for hiring relevance: showcases ML/NLP, API engineering, and cloud deployment in a compact, production-style project.

---

## Features

* **Fast analysis**: TF-IDF semantic baseline + curated skills diff.
* **Actionable output**: strengths, resume-ready improvement bullets, and an optional cover letter (when `detailed=true`).
* **Production-niceties in the UI**:

  * file validation (PDF/DOCX, ≤ **5 MB**), clear errors
  * **Analyze** button auto-disables until inputs are valid
  * **Latency chip** (e.g., “Analyzed • 420 ms”)
  * “**Download JSON**” of results
  * API base indicator (local vs. Render)
* **Switchable embeddings**: start with TF-IDF; swap to Sentence-Transformers or OpenAI with env toggles.
* **Clean REST API** with OpenAPI/Swagger UI.
* **Cloud-ready**: backend on **Render**, frontend on **Vercel**.
* **Tests**: lightweight `pytest` for core scoring & NLP.

---

## Tech Stack

* **Frontend**: React + Vite (fetch → REST), modern responsive UI.
* **Backend**: FastAPI, Uvicorn.
* **NLP**: TF-IDF baseline (scikit-learn), simple skills extractor (extensible).
* **LLM (optional)**: OpenAI for suggestions & cover letter.
* **Cloud**: Render (API) + Vercel (static frontend).
* **Tests**: pytest.

---

## Architecture (high-level)

```
[Browser (Vercel)]  ── fetch ──►  [FastAPI (Render)]
React / Vite                          /api/match (file)
                                      /api/match_text (raw text)
                                      /docs (OpenAPI)

Scoring = 0.4 * semantic (TF-IDF cosine) + 0.6 * skills overlap
Optional LLM suggestions via OpenAI when detailed=true
```

---

## Project Structure

```
backend/
  app.py                 # FastAPI app and routes
  core/
    embed.py             # tfidf | hf | openai backends
    match.py             # score + semantic & overlap calculations
    nlp.py               # skills extraction + synonyms
    parse.py             # PDF/DOCX → text
    suggest.py           # LLM suggestions (OpenAI)
  tests/
    test_match.py        # unit tests
  requirements.txt

frontend/
  src/
    App.jsx              # upload form + results UI
    main.jsx
  vite.config.js
  package.json

README.md
LICENSE (MIT)
```

---

## Local Development

### 1) Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
# http://localhost:8000/docs
```

### 2) Frontend

```bash
cd frontend
npm i
npm run dev
# http://localhost:5173  (Vite proxies /api → http://localhost:8000)
```

---

## Environment Variables

> The backend loads env via `python-dotenv`. Cloud envs are set in provider dashboards.

### Backend (Render)

**Required**

```
OPENAI_API_KEY=sk-...              # needed for detailed suggestions
SUGGESTIONS_MODEL=gpt-4o-mini
ALLOW_ORIGINS=https://ai-job-matcher-beige.vercel.app
```

**Optional (only if switching embeddings)**

```
EMBED_MODE=tfidf                   # tfidf (default) | hf | openai
EMBED_MODEL_HF=sentence-transformers/all-MiniLM-L6-v2
EMBED_MODEL_OPENAI=text-embedding-3-small
```

> Do **not** set `PORT` on Render (Render injects `$PORT` automatically).

### Frontend (Vercel)

```
VITE_API_BASE=https://ai-job-matcher-kw97.onrender.com   # no trailing slash
```

---

## API Reference

### `POST /api/match_text`  (text only)

**Request**

```json
{
  "resume_text": "Built REST APIs in Python; Docker; AWS S3",
  "job_description": "Python + SQL + Docker + AWS",
  "detailed": true
}
```

**Response (example)**

```json
{
  "score": 76.1,
  "semantic_pct": 77.7,
  "overlap_pct": 75.0,
  "top_overlap_skills": ["aws","docker","python"],
  "missing_skills": ["sql"],
  "strengths": ["..."],
  "suggestions": ["..."],
  "cover_letter": "..."
}
```

### `POST /api/match`  (multipart with resume file)

**Form fields**

* `resume_file`: PDF or DOCX (≤ 5 MB)
* `job_description`: string
* `detailed`: `true | false`

**cURL**

```bash
API=https://ai-job-matcher-kw97.onrender.com
curl -X POST "$API/api/match" \
  -F resume_file=@./sample.pdf \
  -F job_description='Python + SQL + Docker + AWS' \
  -F detailed=true
```

---

## How Scoring Works

* **Semantic**: TF-IDF cosine between resume and JD (easy swap for sentence embeddings).
* **Skills overlap**: intersection of extracted skills (see `core/nlp.py` synonyms list).
* **Final score**: `0.4 * semantic + 0.6 * overlap` (tune in `core/match.py`).

---

## Testing

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

---

## Deployment (what’s live now)

* **API (Render)**

  * Root Dir: `backend`
  * Build: `pip install -r requirements.txt`
  * Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
  * Health: `/health`
  * Envs: `OPENAI_API_KEY`, `SUGGESTIONS_MODEL`, `ALLOW_ORIGINS`

* **Frontend (Vercel)**

  * Root Dir: `frontend`
  * Build: `npm run build`
  * Output: `dist`
  * Env: `VITE_API_BASE=https://ai-job-matcher-kw97.onrender.com`

---

## Security & Privacy

* **No resume storage**: files are parsed in-memory for analysis and not persisted.
* **Logs**: avoid logging raw resume/JD content; logs contain only request metadata.
* **CORS**: restricted to the deployed frontend origin.

---

## Roadmap

* ✅ V1: TF-IDF baseline + skills diff + LLM suggestions, cloud deploy
* ⏭ Sentence-Transformers backend & model toggle in UI
* ⏭ Keyword highlighting inside the resume/JD viewer
* ⏭ Auth + saved analyses (Supabase/Firestore)
* ⏭ GitHub Actions CI for tests and lint

---

## License

[MIT](./LICENSE) © Krishna Balaji
