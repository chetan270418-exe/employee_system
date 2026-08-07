from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date, datetime
from app import db
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest, LeaveBalance
from app.models.payroll import Payroll

employee_bp = Blueprint('employee', __name__)


@employee_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    if current_user.role == 'hr':
        return redirect(url_for('hr.dashboard'))

    today = date.today()
    # Today's attendance
    today_att = Attendance.query.filter_by(employee_id=current_user.id, date=today).first()

    # This month attendance
    month_att = Attendance.query.filter(
        Attendance.employee_id == current_user.id,
        db.extract('month', Attendance.date) == today.month,
        db.extract('year', Attendance.date) == today.year
    ).all()
    present_days = sum(1 for a in month_att if a.status in ('present', 'late'))
    
    # Working days this month
    import calendar
    _, days_in_month = calendar.monthrange(today.year, today.month)
    working_days = sum(1 for d in range(1, today.day + 1)
                       if date(today.year, today.month, d).weekday() < 5)
    att_percentage = round((present_days / working_days * 100) if working_days > 0 else 0, 1)

    # Leave balance
    leave_bal = LeaveBalance.query.filter_by(employee_id=current_user.id).first()

    # Latest payroll
    latest_payroll = Payroll.query.filter_by(employee_id=current_user.id).order_by(
        Payroll.year.desc(), Payroll.month.desc()
    ).first()

    # Recent leave requests
    recent_leaves = LeaveRequest.query.filter_by(employee_id=current_user.id).order_by(
        LeaveRequest.applied_on.desc()
    ).limit(5).all()

    # Attendance for last 7 days
    att_history = []
    for i in range(6, -1, -1):
        d = today - __import__('datetime').timedelta(days=i)
        a = Attendance.query.filter_by(employee_id=current_user.id, date=d).first()
        att_history.append({'date': d.strftime('%d %b'), 'status': a.status if a else 'absent'})

    return render_template('employee/dashboard.html',
                           today=today,
                           today_att=today_att,
                           present_days=present_days,
                           working_days=working_days,
                           att_percentage=att_percentage,
                           leave_bal=leave_bal,
                           latest_payroll=latest_payroll,
                           recent_leaves=recent_leaves,
                           att_history=att_history)


@employee_bp.route('/attendance-history')
@login_required
def attendance_history():
    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)
    records = Attendance.query.filter(
        Attendance.employee_id == current_user.id,
        db.extract('month', Attendance.date) == month,
        db.extract('year', Attendance.date) == year
    ).order_by(Attendance.date.desc()).all()
    return render_template('employee/attendance_history.html',
                           records=records, month=month, year=year)


@employee_bp.route('/salary-history')
@login_required
def salary_history():
    payrolls = Payroll.query.filter_by(employee_id=current_user.id).order_by(
        Payroll.year.desc(), Payroll.month.desc()
    ).all()
    return render_template('employee/salary_history.html', payrolls=payrolls)
