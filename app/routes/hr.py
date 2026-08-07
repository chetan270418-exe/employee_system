from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import date
from app import db
from app.models.user import User
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest, LeaveBalance
from app.models.document import AuditLog

hr_bp = Blueprint('hr', __name__)


def hr_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('admin', 'hr'):
            flash('HR access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@hr_bp.route('/dashboard')
@login_required
@hr_required
def dashboard():
    today = date.today()
    total_employees = User.query.filter_by(is_active=True, role='employee').count()
    present_today = Attendance.query.filter_by(date=today, status='present').count()
    late_today = Attendance.query.filter_by(date=today, status='late').count()
    
    pending_leaves = LeaveRequest.query.filter_by(status='pending').order_by(
        LeaveRequest.applied_on.desc()
    ).all()
    
    today_attendance = Attendance.query.filter_by(date=today).all()
    
    return render_template('hr/dashboard.html',
                           total_employees=total_employees,
                           present_today=present_today,
                           late_today=late_today,
                           pending_leaves=pending_leaves,
                           today_attendance=today_attendance,
                           today=today)


@hr_bp.route('/leave-approvals')
@login_required
@hr_required
def leave_approvals():
    status_filter = request.args.get('status', 'pending')
    leaves = LeaveRequest.query.filter_by(status=status_filter).order_by(
        LeaveRequest.applied_on.desc()
    ).all()
    return render_template('hr/leave_approvals.html', leaves=leaves, status_filter=status_filter)


@hr_bp.route('/leave/<int:leave_id>/approve', methods=['POST'])
@login_required
@hr_required
def approve_leave(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    comments = request.form.get('comments', '')
    
    leave.status = 'approved'
    leave.approved_by = current_user.id
    leave.hr_comments = comments
    
    # Deduct from leave balance
    lb = LeaveBalance.query.filter_by(employee_id=leave.employee_id).first()
    if lb:
        if leave.leave_type == 'casual':
            lb.casual_leave = max(0, lb.casual_leave - leave.days)
        elif leave.leave_type == 'sick':
            lb.sick_leave = max(0, lb.sick_leave - leave.days)
        elif leave.leave_type == 'earned':
            lb.earned_leave = max(0, lb.earned_leave - leave.days)
    
    log = AuditLog(user_id=current_user.id, action='APPROVE_LEAVE',
                   target_type='leave', target_id=leave_id,
                   details=f'Approved leave for employee {leave.employee_id}',
                   ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    flash('Leave approved successfully!', 'success')
    return redirect(url_for('hr.leave_approvals'))


@hr_bp.route('/leave/<int:leave_id>/reject', methods=['POST'])
@login_required
@hr_required
def reject_leave(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    comments = request.form.get('comments', '')
    leave.status = 'rejected'
    leave.approved_by = current_user.id
    leave.hr_comments = comments
    log = AuditLog(user_id=current_user.id, action='REJECT_LEAVE',
                   target_type='leave', target_id=leave_id,
                   details=f'Rejected leave for employee {leave.employee_id}',
                   ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    flash('Leave rejected.', 'warning')
    return redirect(url_for('hr.leave_approvals'))


@hr_bp.route('/attendance-management')
@login_required
@hr_required
def attendance_management():
    selected_date = request.args.get('date', str(date.today()))
    try:
        from datetime import datetime
        sel_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except Exception:
        sel_date = date.today()
    
    employees = User.query.filter_by(is_active=True, role='employee').all()
    att_records = {a.employee_id: a for a in Attendance.query.filter_by(date=sel_date).all()}
    
    return render_template('hr/attendance_management.html',
                           employees=employees,
                           att_records=att_records,
                           selected_date=sel_date)


@hr_bp.route('/attendance/manual-mark', methods=['POST'])
@login_required
@hr_required
def manual_mark():
    from datetime import datetime, time
    emp_id = int(request.form.get('employee_id'))
    att_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    status = request.form.get('status', 'present')
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')
    
    existing = Attendance.query.filter_by(employee_id=emp_id, date=att_date).first()
    if existing:
        existing.status = status
        existing.method = 'manual'
        existing.marked_by = current_user.id
        if check_in_str:
            existing.check_in = datetime.strptime(check_in_str, '%H:%M').time()
        if check_out_str:
            existing.check_out = datetime.strptime(check_out_str, '%H:%M').time()
    else:
        att = Attendance(
            employee_id=emp_id,
            date=att_date,
            status=status,
            method='manual',
            marked_by=current_user.id,
            check_in=datetime.strptime(check_in_str, '%H:%M').time() if check_in_str else None,
            check_out=datetime.strptime(check_out_str, '%H:%M').time() if check_out_str else None,
        )
        db.session.add(att)
    db.session.commit()
    flash('Attendance marked successfully!', 'success')
    return redirect(url_for('hr.attendance_management', date=str(att_date)))
