# Resume Match & Job Finder

A beginner-friendly Python/NLP portfolio project that:
- extracts text from PDF, DOCX, and TXT resumes;
- compares a resume with a pasted job description using TF-IDF and cosine similarity;
- identifies matching and potentially missing skills from a small editable vocabulary;
- recommends relevant sample roles from `jobs.json`.

## Important limitations
- Scores are text/skill similarity indicators, not probabilities of being hired.
- The sample job roles are not live vacancies.
- Skill extraction uses a hand-maintained vocabulary and can miss synonyms or context.
- Scanned PDFs may not contain extractable text. OCR is not included.
- This is an educational tool, not an automated hiring decision system.

## Setup (Windows / VS Code)

1. Install Python 3.10+ if you do not already have it.
2. Open this folder in VS Code.
3. In Terminal > New Terminal, create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal instead:

   ```bat
   .venv\Scripts\activate.bat
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Run the app:

   ```powershell
   python app.py
   ```

6. Open the local address printed in the terminal, normally `http://127.0.0.1:5000`.

## Customize
- Add job descriptions and role names to `jobs.json`.
- Add relevant terms and aliases to `SKILLS` in `matcher.py`.
- To make a stronger ML project, prepare labeled job-description examples, train a job-category classifier, and report a held-out test F1 score. Do not report metrics before evaluating the model.

## Suggested GitHub repository contents
Keep `app.py`, `matcher.py`, `jobs.json`, `templates/`, `static/`, `requirements.txt`, and this README. Do not upload real personal resumes or private applicant data.
