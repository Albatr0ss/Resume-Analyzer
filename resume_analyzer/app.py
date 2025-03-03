from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pdfminer.high_level
import docx2txt
from transformers import pipeline  # Import Hugging Face Transformers

app = Flask(__name__)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load Hugging Face summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text(file_path):
    """Extracts text from PDF or DOCX files."""
    if file_path.endswith('.pdf'):
        return pdfminer.high_level.extract_text(file_path)
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    return ""

def generate_feedback(resume_text):
    """Uses Hugging Face model to generate feedback on the resume."""
    if len(resume_text) < 50:
        return "The resume text is too short to analyze. Please upload a more detailed resume."
    
    summary = summarizer(resume_text, max_length=200, min_length=50, do_sample=False)
    return summary[0]['summary_text']

@app.route("/", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        file = request.files['resume']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Extract text from the uploaded resume
            resume_text = extract_text(file_path)

            # Generate feedback using Hugging Face model
            feedback = generate_feedback(resume_text)

            return render_template("result.html", feedback=feedback)

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
