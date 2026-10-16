from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pathlib import Path
import json

from matcher import extract_text_from_file, analyze_resume, recommend_jobs

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
JOBS_FILE = Path(__file__).parent / "jobs.json"


def load_jobs():
    with JOBS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    job_description = ""
    filename = ""

    if request.method == "POST":
        uploaded_file = request.files.get("resume")
        job_description = request.form.get("job_description", "").strip()

        if not uploaded_file or uploaded_file.filename == "":
            error = "Please choose a resume file."
        elif "." not in uploaded_file.filename or uploaded_file.filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS:
            error = "Supported file types: PDF, DOCX, and TXT."
        elif not job_description:
            error = "Please paste a job description."
        else:
            filename = secure_filename(uploaded_file.filename)
            try:
                resume_text = extract_text_from_file(
                    uploaded_file.read(),
                    uploaded_file.filename.rsplit(".", 1)[1].lower()
                )
                if len(resume_text.strip()) < 30:
                    error = "Not enough readable text was found. If this is a scanned PDF, use a text-based PDF or OCR it first."
                else:
                    result = analyze_resume(resume_text, job_description)
                    result["recommendations"] = recommend_jobs(resume_text, load_jobs())
            except Exception as exc:
                # Keep user-facing errors simple; details are printed in the terminal.
                print("Resume processing error:", repr(exc))
                error = "Could not read this file. Try another text-based PDF, DOCX, or TXT file."

    return render_template(
        "index.html",
        result=result,
        error=error,
        job_description=job_description,
        filename=filename
    )


@app.errorhandler(413)
def too_large(_error):
    return render_template(
        "index.html",
        result=None,
        error="File is too large. Please upload a file smaller than 5 MB.",
        job_description="",
        filename=""
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
