import React, { useCallback, useRef, useState } from "react";

export default function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [detailed, setDetailed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const API_BASE = import.meta.env.VITE_API_BASE || ""; // e.g. "https://your-api.onrender.com"


  const dropRef = useRef(null);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    const f = e.dataTransfer.files?.[0];
    if (f && isAllowedFile(f)) {
      setResumeFile(f);
    } else {
      setError("Please drop a .pdf or .docx file.");
    }
  }, []);

  const isAllowedFile = (f) =>
    /\.(pdf|docx)$/i.test(f?.name || "") ||
    ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"].includes(
      f?.type || ""
    );

  const onSubmit = async (e) => {
    e?.preventDefault();
    setError("");
    setResult(null);

    if (!resumeFile || !jdText.trim()) {
      setError("Please upload a resume and paste a job description.");
      return;
    }

    const fd = new FormData();
    fd.append("resume_file", resumeFile);
    fd.append("job_description", jdText);
    fd.append("detailed", detailed ? "true" : "false");

    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/match`, { method: 'POST', body: fd })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${resp.status})`);
      }
      const data = await resp.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const loadSampleJD = () => {
    setJdText(
      `We’re hiring a Python Backend Engineer with experience in SQL, Docker, and AWS. 
Responsibilities include building REST APIs, integrating data stores, and deploying services with CI/CD.`
    );
  };

  const clearAll = () => {
    setResumeFile(null);
    setJdText("");
    setDetailed(false);
    setResult(null);
    setError("");
  };

  const fitInfo = (score) => {
    if (score >= 85) return { label: "Excellent", tone: "good" };
    if (score >= 70) return { label: "Strong", tone: "ok" };
    if (score >= 50) return { label: "Medium", tone: "warn" };
    return { label: "Low", tone: "bad" };
  };

  const handleBrowse = (e) => {
    const f = e.target.files?.[0];
    if (f && isAllowedFile(f)) {
      setResumeFile(f);
    } else if (f) {
      setError("Please choose a .pdf or .docx file.");
      e.target.value = null;
    }
  };

  return (
    <div className="page">
      <header className="nav">
        <div className="nav__brand">
          <span className="logo">AI</span>
          <span>Job Matcher</span>
        </div>
        <div className="nav__actions">
          <a
            href="http://localhost:8080/docs"
            target="_blank"
            rel="noreferrer"
            className="button button--ghost"
          >
            API Docs
          </a>
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <h1>Get a job-specific resume match — instantly</h1>
          <p className="muted">
            Upload your <strong>PDF/DOCX</strong>, paste a job description, and get a{" "}
            <strong>match score</strong>, overlapping/missing skills, and (optionally){" "}
            resume-ready suggestions.
          </p>
        </section>

        <section className="grid">
          {/* Left column — form */}
          <div className="card">
            <h2 className="card__title">Analyze a match</h2>
            <form onSubmit={onSubmit} className="form">
              <div
                ref={dropRef}
                className="dropzone"
                onDragOver={(e) => {
                  e.preventDefault();
                  dropRef.current?.classList.add("dropzone--active");
                }}
                onDragLeave={() => dropRef.current?.classList.remove("dropzone--active")}
                onDrop={(e) => {
                  dropRef.current?.classList.remove("dropzone--active");
                  onDrop(e);
                }}
              >
                <input
                  id="resume-file"
                  type="file"
                  accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={handleBrowse}
                  hidden
                />
                <p className="dropzone__label">
                  {resumeFile ? (
                    <>
                      <span className="file-name">{resumeFile.name}</span>
                      <button
                        type="button"
                        onClick={() => setResumeFile(null)}
                        className="chip chip--danger"
                        aria-label="Remove file"
                      >
                        Remove
                      </button>
                    </>
                  ) : (
                    <>
                      <strong>Drag &amp; drop</strong> your resume here, or{" "}
                      <label htmlFor="resume-file" className="link">
                        browse
                      </label>{" "}
                      (.pdf/.docx)
                    </>
                  )}
                </p>
              </div>

              <label className="field">
                <div className="field__label">Job Description</div>
                <textarea
                  rows={10}
                  placeholder="Paste the job description here…"
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />
                <div className="field__hint">
                  <button type="button" className="link" onClick={loadSampleJD}>
                    Use sample JD
                  </button>
                  <span className="muted">{jdText.length} chars</span>
                </div>
              </label>

              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={detailed}
                  onChange={(e) => setDetailed(e.target.checked)}
                />
                <span>Request detailed suggestions (requires API key)</span>
              </label>

              <div className="form__actions">
                <button className="button" type="submit" disabled={loading}>
                  {loading ? "Analyzing…" : "Analyze"}
                </button>
                <button
                  className="button button--ghost"
                  type="button"
                  disabled={loading}
                  onClick={clearAll}
                >
                  Reset
                </button>
              </div>

              {error && (
                <div role="alert" className="alert alert--error">
                  {error}
                </div>
              )}
            </form>
          </div>

          {/* Right column — results */}
          <div className="card">
            <h2 className="card__title">Results</h2>

            {!result && (
              <div className="placeholder">
                <p className="muted">
                  Results will appear here after you analyze a resume + job description.
                </p>
              </div>
            )}

            {result && (
              <>
                <div className="score">
                  <div className="score__row">
                    <div className="score__big">
                      {Math.round(result.score)}%
                      <span className="score__label">Match Score</span>
                    </div>
                    <span className={`chip chip--${fitInfo(result.score).tone}`}>
                      Fit: {fitInfo(result.score).label}
                    </span>
                  </div>

                  <div className="progress">
                    <div
                      className="progress__bar"
                      style={{ width: `${Math.min(100, Math.max(0, Math.round(result.score)))}%` }}
                    />
                  </div>

                  <div className="kpis">
                    <div className="kpi">
                      <div className="kpi__value">{Math.round(result.semantic_pct)}%</div>
                      <div className="kpi__label">Semantic</div>
                    </div>
                    <div className="kpi">
                      <div className="kpi__value">{Math.round(result.overlap_pct)}%</div>
                      <div className="kpi__label">Skills Overlap</div>
                    </div>
                  </div>
                </div>

                <div className="split">
                  <section>
                    <h3>Overlapping Skills</h3>
                    <div className="badges">
                      {(result.top_overlap_skills || []).length ? (
                        result.top_overlap_skills.map((s, i) => (
                          <span key={i} className="badge">
                            {s}
                          </span>
                        ))
                      ) : (
                        <p className="muted">No overlaps detected.</p>
                      )}
                    </div>
                  </section>

                  <section>
                    <h3>Missing Skills</h3>
                    <div className="badges">
                      {(result.missing_skills || []).length ? (
                        result.missing_skills.map((s, i) => (
                          <span key={i} className="badge badge--warn">
                            {s}
                          </span>
                        ))
                      ) : (
                        <p className="muted">No obvious gaps found.</p>
                      )}
                    </div>
                  </section>
                </div>

                {!!(result.strengths || []).length && (
                  <section>
                    <h3>Strengths</h3>
                    <ul className="list">
                      {result.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </section>
                )}

                {!!(result.suggestions || []).length && (
                  <section>
                    <h3>Suggestions (resume-ready)</h3>
                    <ul className="list">
                      {result.suggestions.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </section>
                )}

                {result.cover_letter && (
                  <section>
                    <h3>Cover Letter</h3>
                    <textarea readOnly rows={6} value={result.cover_letter} />
                    <div className="form__actions" style={{ marginTop: 8 }}>
                      <button
                        type="button"
                        className="button button--ghost"
                        onClick={() => navigator.clipboard.writeText(result.cover_letter)}
                      >
                        Copy cover letter
                      </button>
                    </div>
                  </section>
                )}
              </>
            )}
          </div>
        </section>

        <footer className="footer">
          <span className="muted">
            Built with FastAPI + React. Embeddings: TF-IDF (switchable to Sentence-Transformers or OpenAI).
          </span>
        </footer>
      </main>
    </div>
  );
}
