from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, datetime, timedelta
from app import db
from app.models.user import User, Department
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest, LeaveBalance
from app.models.payroll import Payroll
from app.models.document import AuditLog

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    today = date.today()
    total_employees = User.query.filter_by(is_active=True, role='employee').count()
    present_today = Attendance.query.filter_by(date=today, status='present').count()
    absent_today = total_employees - present_today
    
    # Monthly payroll cost
    current_month_payrolls = Payroll.query.filter_by(
        month=today.month, year=today.year
    ).all()
    monthly_cost = sum(float(p.net_salary) for p in current_month_payrolls)

    # Department-wise count
    departments = Department.query.all()
    dept_data = []
    for dept in departments:
        count = User.query.filter_by(department_id=dept.id, is_active=True, role='employee').count()
        dept_data.append({'name': dept.name, 'count': count})

    # Attendance for last 7 days
    att_chart = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        p = Attendance.query.filter_by(date=d, status='present').count()
        att_chart.append({'date': d.strftime('%d %b'), 'count': p})

    # Recent employees
    recent_employees = User.query.filter_by(is_active=True, role='employee').order_by(
        User.created_at.desc()
    ).limit(5).all()

    # Pending leaves
    pending_leaves = LeaveRequest.query.filter_by(status='pending').count()

    return render_template('admin/dashboard.html',
                           total_employees=total_employees,
                           present_today=present_today,
                           absent_today=absent_today,
                           monthly_cost=monthly_cost,
                           dept_data=dept_data,
                           att_chart=att_chart,
                           recent_employees=recent_employees,
                           pending_leaves=pending_leaves,
                           today=today)


@admin_bp.route('/employees')
@login_required
@admin_required
def employees():
    dept_id = request.args.get('dept', type=int)
    search = request.args.get('q', '')
    query = User.query.filter_by(is_active=True).filter(User.role.in_(['employee', 'hr']))
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if search:
        query = query.filter(User.name.ilike(f'%{search}%') | User.employee_id.ilike(f'%{search}%'))
    employees = query.order_by(User.name).all()
    departments = Department.query.all()
    return render_template('admin/employees.html', employees=employees,
                           departments=departments, search=search, dept_id=dept_id)


@admin_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    departments = Department.query.all()
    if request.method == 'POST':
        f = request.form
        # Check duplicate email
        if User.query.filter_by(email=f['email']).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/employee_form.html', departments=departments, employee=None)
        
        # Auto-generate employee ID
        count = User.query.count() + 1
        emp_id = f'EMP{str(count).zfill(4)}'
        while User.query.filter_by(employee_id=emp_id).first():
            count += 1
            emp_id = f'EMP{str(count).zfill(4)}'

        emp = User(
            employee_id=emp_id,
            name=f['name'],
            email=f['email'].lower(),
            role=f.get('role', 'employee'),
            phone=f.get('phone'),
            address=f.get('address'),
            gender=f.get('gender'),
            department_id=f.get('department_id') or None,
            designation=f.get('designation'),
            employment_type=f.get('employment_type', 'full_time'),
            base_salary=float(f.get('base_salary', 0)),
            bank_account=f.get('bank_account'),
            bank_name=f.get('bank_name'),
            pan_number=f.get('pan_number'),
            aadhaar_number=f.get('aadhaar_number'),
        )
        if f.get('date_of_birth'):
            emp.date_of_birth = datetime.strptime(f['date_of_birth'], '%Y-%m-%d').date()
        if f.get('join_date'):
            emp.join_date = datetime.strptime(f['join_date'], '%Y-%m-%d').date()
        emp.set_password(f.get('password', 'Welcome@123'))
        db.session.add(emp)
        db.session.flush()

        # Create leave balance
        lb = LeaveBalance(employee_id=emp.id)
        db.session.add(lb)
        
        log = AuditLog(user_id=current_user.id, action='ADD_EMPLOYEE',
                       target_type='user', target_id=emp.id,
                       details=f'Added employee {emp.name}', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        flash(f'Employee {emp.name} added! ID: {emp_id}, Default password: Welcome@123', 'success')
        return redirect(url_for('admin.employees'))
    return render_template('admin/employee_form.html', departments=departments, employee=None)


@admin_bp.route('/employees/<int:emp_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(emp_id):
    emp = User.query.get_or_404(emp_id)
    departments = Department.query.all()
    if request.method == 'POST':
        f = request.form
        emp.name = f.get('name', emp.name)
        emp.phone = f.get('phone', emp.phone)
        emp.address = f.get('address', emp.address)
        emp.gender = f.get('gender', emp.gender)
        emp.department_id = f.get('department_id') or None
        emp.designation = f.get('designation', emp.designation)
        emp.employment_type = f.get('employment_type', emp.employment_type)
        emp.base_salary = float(f.get('base_salary', emp.base_salary))
        emp.bank_account = f.get('bank_account', emp.bank_account)
        emp.bank_name = f.get('bank_name', emp.bank_name)
        emp.pan_number = f.get('pan_number', emp.pan_number)
        emp.aadhaar_number = f.get('aadhaar_number', emp.aadhaar_number)
        emp.role = f.get('role', emp.role)
        if f.get('date_of_birth'):
            emp.date_of_birth = datetime.strptime(f['date_of_birth'], '%Y-%m-%d').date()
        if f.get('join_date'):
            emp.join_date = datetime.strptime(f['join_date'], '%Y-%m-%d').date()
        new_pass = f.get('new_password')
        if new_pass and len(new_pass) >= 6:
            emp.set_password(new_pass)
        log = AuditLog(user_id=current_user.id, action='EDIT_EMPLOYEE',
                       target_type='user', target_id=emp.id,
                       details=f'Edited employee {emp.name}', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('admin.employee_detail', emp_id=emp.id))
    return render_template('admin/employee_form.html', departments=departments, employee=emp)


@admin_bp.route('/employees/<int:emp_id>')
@login_required
@admin_required
def employee_detail(emp_id):
    emp = User.query.get_or_404(emp_id)
    today = date.today()
    att_this_month = Attendance.query.filter(
        Attendance.employee_id == emp_id,
        db.extract('month', Attendance.date) == today.month,
        db.extract('year', Attendance.date) == today.year
    ).all()
    recent_payrolls = Payroll.query.filter_by(employee_id=emp_id).order_by(
        Payroll.year.desc(), Payroll.month.desc()
    ).limit(6).all()
    recent_leaves = LeaveRequest.query.filter_by(employee_id=emp_id).order_by(
        LeaveRequest.applied_on.desc()
    ).limit(5).all()
    leave_bal = LeaveBalance.query.filter_by(employee_id=emp_id).first()
    return render_template('admin/employee_detail.html', emp=emp,
                           att_this_month=att_this_month,
                           recent_payrolls=recent_payrolls,
                           recent_leaves=recent_leaves,
                           leave_bal=leave_bal)


@admin_bp.route('/employees/<int:emp_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_employee(emp_id):
    emp = User.query.get_or_404(emp_id)
    emp.is_active = False
    log = AuditLog(user_id=current_user.id, action='DEACTIVATE_EMPLOYEE',
                   target_type='user', target_id=emp.id,
                   details=f'Deactivated {emp.name}', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    flash(f'{emp.name} has been deactivated.', 'warning')
    return redirect(url_for('admin.employees'))


@admin_bp.route('/departments', methods=['GET', 'POST'])
@login_required
@admin_required
def departments():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()
        if name:
            dept = Department(name=name, description=desc)
            db.session.add(dept)
            db.session.commit()
            flash(f'Department "{name}" created!', 'success')
    depts = Department.query.order_by(Department.name).all()
    return render_template('admin/departments.html', departments=depts)


@admin_bp.route('/audit-log')
@login_required
@admin_required
def audit_log():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=30)
    return render_template('admin/audit_log.html', logs=logs)
