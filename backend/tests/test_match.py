from core.match import compute_score
from core.embed import TFIDFEmbedder
from core.nlp import extract_skills_simple, find_missing_skills_simple

def test_identical_text_high_score():
    text = "Python SQL Docker AWS built REST API"
    score, sem, ovlp, _ = compute_score(text, text, TFIDFEmbedder())
    assert sem > 90
    assert score > 90

def test_unrelated_text_low_score():
    a = "I love cooking Italian pasta and traveling in Europe."
    b = "Distributed systems with Kubernetes, Docker, and AWS"
    score, sem, ovlp, _ = compute_score(a, b, TFIDFEmbedder())
    assert sem < 60  # semantic can still find some english overlap; keep threshold loose

def test_missing_skills():
    jd = "We require Python, SQL, and Docker"
    resume = "Experience with Python and REST"
    jd_s = extract_skills_simple(jd)
    res_s = extract_skills_simple(resume)
    miss = find_missing_skills_simple(jd_s, res_s)
    assert "sql" in miss or "docker" in miss

def test_sql_synonyms_count_as_sql():
    jd = "We require SQL and Docker"
    resume = "Experience with PostgreSQL and Docker in production"
    jd_s = extract_skills_simple(jd)
    res_s = extract_skills_simple(resume)
    miss = find_missing_skills_simple(jd_s, res_s)
    assert "sql" not in miss  # postgres/postgresql should normalize to sql
