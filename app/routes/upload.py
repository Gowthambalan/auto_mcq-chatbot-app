# 

from fastapi import APIRouter, UploadFile, File
from app.services.extractor import generate_pdf_log
from app.services.subject_classifier import detect_subject_from_text
from pathlib import Path
import shutil
import os
import json
from datetime import datetime

router = APIRouter()

BASE_UPLOAD_DIR = Path("data/uploads")
BASE_LOG_DIR = Path("data/logs")
SESSION_FILE = Path("data/session/recent_uploads.json")

# Ensure directories exist
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
BASE_LOG_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

@router.post("/upload_pdfs")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    uploaded_files = []

    for file in files:
        # Save temporarily to detect subject
        temp_path = BASE_UPLOAD_DIR / file.filename
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Generate log + extract text
        pdf_log, preview_text = generate_pdf_log(str(temp_path))
        subject = detect_subject_from_text(preview_text) or "unknown"

        # Create subject directories
        subject_upload_dir = BASE_UPLOAD_DIR / subject
        subject_log_dir = BASE_LOG_DIR / subject
        subject_upload_dir.mkdir(parents=True, exist_ok=True)
        subject_log_dir.mkdir(parents=True, exist_ok=True)

        # Move file to final path
        final_path = subject_upload_dir / file.filename
        shutil.move(str(temp_path), final_path)

        # Create log entry
        log_entry = {
            "filename": file.filename,
            "path": str(final_path),
            "log": pdf_log,
            "subject": subject,
            "status": "uploaded",
            "timestamp": datetime.now().isoformat()
        }

        # Save log file
        log_file = subject_log_dir / f"{file.filename}.json"
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)

        uploaded_files.append(log_entry)

    # Save current session upload filenames
    with open(SESSION_FILE, "w") as f:
        json.dump([entry["filename"] for entry in uploaded_files], f)

    return {"uploaded_files": uploaded_files}
