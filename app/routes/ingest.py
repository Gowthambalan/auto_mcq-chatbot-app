from fastapi import APIRouter, Body
from app.services.vector_store import ingest_to_vector_db
from pathlib import Path
from datetime import datetime
import json
import re

router = APIRouter()
LOG_DIR = Path("data/logs")
SESSION_FILE = Path("data/session/recent_uploads.json")


def extract_log_details(log_text: str):
    """Extract file, pages, format, and size from log text."""
    file_match = re.search(r"File:\s*(.+)", log_text)
    pages_match = re.search(r"Pages:\s*(\d+)", log_text)
    format_match = re.search(r"'format':\s*'([^']+)'", log_text)
    size_match = re.search(r"'file_size':\s*'([^']+)'", log_text)

    return {
        "file": file_match.group(1) if file_match else "unknown",
        "pages": int(pages_match.group(1)) if pages_match else 0,
        "format": format_match.group(1) if format_match else "unknown",
        "file_size": size_match.group(1) if size_match else "unknown"
    }


@router.get("/uploaded_pdfs")
def list_uploaded_pdfs():
    if not SESSION_FILE.exists():
        return {"files": []}

    with open(SESSION_FILE, "r") as f:
        recent_filenames = set(json.load(f))

    files = []
    for log_file in LOG_DIR.rglob("*.json"):
        with open(log_file, "r") as f:
            entry = json.load(f)

        if entry["filename"] not in recent_filenames:
            continue

        log_text = entry.get("log", "")
        log_details = extract_log_details(log_text)

        files.append({
            "filename": entry["filename"],
            "subject": entry.get("subject", "unknown"),
            "status": entry.get("status", "unknown"),
            "log": log_details
        })

    return {"files": files}


@router.post("/ingest_pdfs")
def ingest_selected_or_all_pdfs(filenames: list[str] = Body(...)):
    """Ingest selected or all session-uploaded PDFs to vector DB."""
    if not SESSION_FILE.exists():
        return {"results": [], "message": "No session found"}

    with open(SESSION_FILE, "r") as f:
        session_files = set(json.load(f))

    # If "all" is passed or empty list is passed, ingest all from session
    if not filenames or filenames == ["all"]:
        target_files = session_files
    else:
        target_files = set(filenames).intersection(session_files)

    results = []

    for log_file in LOG_DIR.rglob("*.json"):
        with open(log_file, "r") as f:
            entry = json.load(f)

        if entry["filename"] not in target_files:
            continue

        pdf_path = entry["path"]
        subject = entry.get("subject", "unknown")

        success = ingest_to_vector_db(pdf_path, subject)
        if success:
            entry["status"] = "ingested"
            with open(log_file, "w") as f:
                json.dump(entry, f, indent=2)

        results.append({
            "filename": entry["filename"],
            "status": "ingested" if success else "failed"
        })

    return {"results": results}
