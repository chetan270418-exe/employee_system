"""
Storage Service — Local file storage (drop-in replacement for S3)
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, subfolder='documents'):
    """Save a file to local storage and return the path."""
    if not file or not allowed_file(file.filename):
        return None, None
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, stored_name)
    file.save(full_path)
    return stored_name, full_path


def delete_file(file_path):
    """Delete a file from local storage."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def get_file_url(subfolder, stored_name):
    """Return a URL path to serve the file."""
    return f'/uploads/{subfolder}/{stored_name}'
