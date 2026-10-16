import io
import re
from docx import Document
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# This is a simple editable skills vocabulary for the demo.
# Expand it with synonyms and skills relevant to your target roles.
SKILLS = [
    "python", "java", "c++", "c", "sql", "excel", "power bi", "tableau",
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "machine learning",
    "deep learning", "nlp", "natural language processing", "flask", "django",
    "html", "css", "javascript", "react", "git", "github", "linux",
    "data analysis", "data visualization", "statistics", "tensorflow", "pytorch",
    "aws", "azure", "docker", "mongodb", "mysql", "postgresql",
    "communication", "problem solving", "teamwork"
]


def extract_text_from_file(file_bytes: bytes, extension: str) -> str:
    """Extract text from PDF, DOCX, or plain text bytes."""
    extension = extension.lower()

    if extension == "pdf":
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            return "\n".join(page.get_text() for page in pdf)

    if extension == "docx":
        document = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in document.paragraphs]
        # Also extract table cells, since resumes often use tables.
        for table in document.tables:
            for row in table.rows:
                paragraphs.append(" ".join(cell.text for cell in row.cells))
        return "\n".join(paragraphs)

    if extension == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    raise ValueError("Unsupported file type")


def clean_text(text: str) -> str:
    """Basic normalization; preserve useful punctuation in skill names."""
    text = text.lower()
    text = text.replace("machine-learning", "machine learning")
    text = text.replace("scikit learn", "scikit-learn")
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text: str) -> list[str]:
    """Return vocabulary skills found as whole terms in text."""
    normalized = clean_text(text)
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(set(found))


def text_similarity(text_a: str, text_b: str) -> float:
    """TF-IDF cosine similarity, returned as a percentage."""
    a = clean_text(text_a)
    b = clean_text(text_b)
    if not a or not b:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([a, b])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(float(score) * 100, 1)


def analyze_resume(resume_text: str, job_description: str) -> dict:
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched = sorted(set(resume_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(resume_skills))
    similarity = text_similarity(resume_text, job_description)

    # This is a transparent heuristic, not a hiring probability.
    # It combines text similarity and skill coverage for a simple demo.
    if job_skills:
        skill_coverage = len(matched) / len(job_skills) * 100
        match_score = round(0.65 * similarity + 0.35 * skill_coverage, 1)
    else:
        skill_coverage = 0.0
        match_score = similarity

    return {
        "similarity": similarity,
        "skill_coverage": round(skill_coverage, 1),
        "match_score": min(100.0, max(0.0, match_score)),
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched,
        "missing_skills": missing,
    }


def recommend_jobs(resume_text: str, jobs: list[dict], limit: int = 5) -> list[dict]:
    """Rank sample job roles by resume/job-description text similarity."""
    ranked = []
    for job in jobs:
        score = text_similarity(resume_text, job["description"])
        resume_skills = set(extract_skills(resume_text))
        job_skills = set(extract_skills(job["description"]))
        if job_skills:
            coverage = len(resume_skills & job_skills) / len(job_skills) * 100
            score = round(0.65 * score + 0.35 * coverage, 1)
        ranked.append({
            "title": job["title"],
            "description": job["description"],
            "score": score,
            "skills": sorted(job_skills),
        })

    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
