from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from datetime import datetime
import os
from app import db
from app.models.document import Document
from app.models.user import User
from app.services.storage_service import save_file, delete_file, allowed_file

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/')
@login_required
def index():
    if current_user.role in ('admin', 'hr'):
        emp_id = request.args.get('emp_id', current_user.id, type=int)
    else:
        emp_id = current_user.id
    emp = User.query.get_or_404(emp_id)
    docs = Document.query.filter_by(employee_id=emp_id).order_by(Document.uploaded_on.desc()).all()
    employees = User.query.filter_by(is_active=True).all() if current_user.role in ('admin', 'hr') else []
    return render_template('documents/index.html', docs=docs, emp=emp, employees=employees, emp_id=emp_id)


@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if current_user.role in ('admin', 'hr'):
        emp_id = int(request.form.get('employee_id', current_user.id))
    else:
        emp_id = current_user.id
    
    file = request.files.get('file')
    doc_type = request.form.get('doc_type', 'other')
    
    if not file or file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('documents.index', emp_id=emp_id))
    
    if not allowed_file(file.filename):
        flash('File type not allowed.', 'danger')
        return redirect(url_for('documents.index', emp_id=emp_id))
    
    stored_name, full_path = save_file(file, 'documents')
    if not stored_name:
        flash('Failed to save file.', 'danger')
        return redirect(url_for('documents.index', emp_id=emp_id))
    
    doc = Document(
        employee_id=emp_id,
        doc_type=doc_type,
        original_filename=file.filename,
        stored_filename=stored_name,
        file_path=full_path,
        file_size=os.path.getsize(full_path),
        mime_type=file.mimetype,
        uploaded_by=current_user.id
    )
    db.session.add(doc)
    db.session.commit()
    flash('Document uploaded successfully!', 'success')
    return redirect(url_for('documents.index', emp_id=emp_id))


@documents_bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if current_user.role == 'employee' and doc.employee_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('documents.index'))
    if not os.path.exists(doc.file_path):
        flash('File not found.', 'danger')
        return redirect(url_for('documents.index', emp_id=doc.employee_id))
    return send_file(doc.file_path, as_attachment=True, download_name=doc.original_filename)


@documents_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_doc(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if current_user.role == 'employee' and doc.employee_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('documents.index'))
    emp_id = doc.employee_id
    delete_file(doc.file_path)
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted.', 'info')
    return redirect(url_for('documents.index', emp_id=emp_id))
