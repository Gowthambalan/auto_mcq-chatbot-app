# import fitz  # PyMuPDF
# import os
# from datetime import datetime

# def generate_pdf_log(pdf_path):
#     doc = fitz.open(pdf_path)
#     metadata = doc.metadata
#     file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
#     metadata["file_size"] = f"{file_size_mb:.2f} MB"

#     log_lines = [
#         f"=== PDF Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===",
#         f"File: {os.path.basename(pdf_path)}",
#         f"Pages: {len(doc)}",
#         f"Metadata: {metadata}",
#         ""
#     ]

#     all_text = ""
#     for i, page in enumerate(doc):
#         text = page.get_text()
#         all_text += text
#         images = page.get_images(full=True)
#         log_lines.append(f"Page {i+1}:")
#         log_lines.append(f"  - Text length: {len(text)} chars")
#         log_lines.append(f"  - Images: {len(images)}\n")

#     doc.close()
#     return "\n".join(log_lines), all_text[:3000]  # Return preview for subject classification


import fitz  # PyMuPDF
import os
from datetime import datetime

def generate_pdf_log(pdf_path):
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    metadata["file_size"] = f"{file_size_mb:.2f} MB"

    log_lines = [
        f"=== PDF Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===",
        f"File: {os.path.basename(pdf_path)}",
        f"Pages: {len(doc)}",
        f"Metadata: {metadata}",
        ""
    ]

    all_text = ""
    for i, page in enumerate(doc):
        text = page.get_text()
        all_text += text
        images = page.get_images(full=True)
        log_lines.append(f"Page {i+1}:")
        log_lines.append(f"  - Text length: {len(text)} chars")
        log_lines.append(f"  - Images: {len(images)}\n")

    doc.close()
    return "\n".join(log_lines), all_text[:3000]  # Return preview text for subject detection
