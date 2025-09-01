import tempfile
from typing import Optional
from fastapi import UploadFile
import fitz  # PyMuPDF
import docx2txt

async def extract_text_from_upload(upload: UploadFile) -> str:
    if upload.content_type == "application/pdf":
        data = await upload.read()
        with fitz.open(stream=data, filetype="pdf") as doc:
            parts = []
            for page in doc:
                parts.append(page.get_text("text"))
        return "\n".join(parts).strip()

    if upload.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        data = await upload.read()
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            text = docx2txt.process(tmp.name) or ""
        return text.strip()

    raise ValueError("Unsupported file type")
