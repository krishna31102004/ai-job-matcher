import re

TECH_SKILLS = {
    "python","java","c","c++","c#","javascript","typescript","go","rust","swift","kotlin",
    "html","css","react","nextjs","node","express","django","flask","fastapi","spring",
    "sql","mysql","postgres","postgresql","mssql","sqlserver","sqlite",
    "mongodb","redis","graphql","rest","api",
    "aws","amazon web services","gcp","azure","lambda","s3","ec2","iam","docker","kubernetes","terraform",
    "linux","bash","git","github","gitlab","ci/cd","ci","cd","pytest","unittest",
    "numpy","pandas","scikit-learn","sklearn","matplotlib","pytorch","tensorflow","keras",
    "nlp","llm","huggingface","transformers","bert","gpt","xgboost","lightgbm",
    "airflow","spark","hadoop","kafka","tableau","powerbi","power bi","excel",
    "firebase","supabase","vercel","render","heroku"
}

ALIASES = {
    "postgres": "sql",
    "postgresql": "sql",
    "mysql": "sql",
    "mssql": "sql",
    "sqlserver": "sql",
    "amazon": "aws",
    "amazon web services": "aws",
}

def _tokenize_lower(text: str):
    return re.findall(r"[a-zA-Z0-9+#\.]+", text.lower())

def _normalize(tokens):
    out = set()
    for t in tokens:
        t = ALIASES.get(t, t)
        out.add(t)
    if "powerbi" in out:
        out.add("power bi")
    return out

def extract_skills_simple(text: str):
    tokens = _normalize(set(_tokenize_lower(text)))
    return {t for t in tokens if t in TECH_SKILLS}

def find_missing_skills_simple(jd_skills, resume_skills):
    return sorted(list(jd_skills - resume_skills))
