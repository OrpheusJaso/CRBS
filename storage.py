"""File upload helper shared by booking documents (US04) and issue images (US07).

Files are saved to the on-disk UPLOAD_FOLDER (see config.py) under a unique,
secured name; only the stored filename is kept in the database. A matching
download route lives in blueprints/views/views.py (`/uploads/<filename>`).
"""
import os
import uuid

from werkzeug.utils import secure_filename
from flask import current_app, abort

# Supporting documents for booking approval (proposals, letters, slides).
DOC_EXTS = {"pdf", "doc", "docx", "png", "jpg", "jpeg"}
# Photographic evidence for issue reports.
IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "webp"}


def _ext(filename):
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def save_upload(file, allowed):
    """Persist an uploaded file and return its stored filename, or None.

    `file` is a Werkzeug FileStorage (request.files.get(...)). Returns None when
    no file was provided; aborts 400 on an unsupported extension.
    """
    if not file or not file.filename:
        return None
    ext = _ext(file.filename)
    if ext not in allowed:
        abort(400, description="Unsupported file type.")

    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    stored = f"{uuid.uuid4().hex[:12]}_{secure_filename(file.filename)}"
    file.save(os.path.join(folder, stored))
    return stored
