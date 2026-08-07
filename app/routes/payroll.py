from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, datetime
import os
from app import db
from app.models.user import User
from app.models.payroll import Payroll
from app.services.payroll_engine import generate_payroll
from app.services.pdf_generator import generate_salary_slip

payroll_bp = Blueprint('payroll', __name__)


def admin_or_hr(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('admin', 'hr'):
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@payroll_bp.route('/')
@login_required
@admin_or_hr
def index():
    today = date.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)
    payrolls = Payroll.query.filter_by(month=month, year=year).all()
    employees = User.query.filter_by(is_active=True, role='employee').all()
    generated_ids = {p.employee_id for p in payrolls}
    return render_template('payroll/index.html',
                           payrolls=payrolls,
                           employees=employees,
                           generated_ids=generated_ids,
                           month=month, year=year)


@payroll_bp.route('/generate', methods=['POST'])
@login_required
@admin_or_hr
def generate():
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    emp_ids = request.form.getlist('employee_ids')
    bonus = float(request.form.get('bonus', 0))
    other_ded = float(request.form.get('other_deductions', 0))
    
    generated = 0
    skipped = 0
    for emp_id in emp_ids:
        emp = User.query.get(int(emp_id))
        if emp:
            payroll, status = generate_payroll(emp, month, year, bonus, other_ded, current_user.id)
            if status == 'created':
                generated += 1
            else:
                skipped += 1
    
    flash(f'Payroll generated: {generated} new, {skipped} already existed.', 'success')
    return redirect(url_for('payroll.index', month=month, year=year))


@payroll_bp.route('/generate-all', methods=['POST'])
@login_required
@admin_or_hr
def generate_all():
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    bonus = float(request.form.get('bonus', 0))
    other_ded = float(request.form.get('other_deductions', 0))
    employees = User.query.filter_by(is_active=True, role='employee').all()
    generated = 0
    skipped = 0
    for emp in employees:
        _, status = generate_payroll(emp, month, year, bonus, other_ded, current_user.id)
        if status == 'created':
            generated += 1
        else:
            skipped += 1
    flash(f'Bulk payroll: {generated} generated, {skipped} skipped.', 'success')
    return redirect(url_for('payroll.index', month=month, year=year))


@payroll_bp.route('/view/<int:payroll_id>')
@login_required
def view_payroll(payroll_id):
    p = Payroll.query.get_or_404(payroll_id)
    if current_user.role == 'employee' and p.employee_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('employee.dashboard'))
    import calendar
    month_name = calendar.month_name[p.month]
    return render_template('payroll/view.html', payroll=p, month_name=month_name)


@payroll_bp.route('/slip/<int:payroll_id>')
@login_required
def download_slip(payroll_id):
    p = Payroll.query.get_or_404(payroll_id)
    if current_user.role == 'employee' and p.employee_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    from flask import current_app
    slip_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'slips')
    os.makedirs(slip_dir, exist_ok=True)
    import calendar
    slip_filename = f'salary_slip_{p.employee.employee_id}_{calendar.month_abbr[p.month]}_{p.year}.pdf'
    slip_path = os.path.join(slip_dir, slip_filename)
    
    if not os.path.exists(slip_path):
        generate_salary_slip(p, p.employee, slip_path)
        p.slip_path = slip_path
        db.session.commit()
    
    return send_file(slip_path, as_attachment=True, download_name=slip_filename, mimetype='application/pdf')


@payroll_bp.route('/mark-paid/<int:payroll_id>', methods=['POST'])
@login_required
@admin_or_hr
def mark_paid(payroll_id):
    p = Payroll.query.get_or_404(payroll_id)
    p.status = 'paid'
    p.paid_on = datetime.utcnow()
    db.session.commit()
    flash(f'Payroll for {p.employee.name} marked as paid!', 'success')
    return redirect(url_for('payroll.view_payroll', payroll_id=payroll_id))
