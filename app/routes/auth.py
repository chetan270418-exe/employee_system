from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, Department
from app.models.document import AuditLog
from app.models.leave import LeaveBalance
import random

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        user = User.query.filter_by(email=email, is_active=True).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            log = AuditLog(user_id=user.id, action='LOGIN', details=f'{user.name} logged in',
                           ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for(f'{user.role}.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))
    
    departments = Department.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        department_id = request.form.get('department_id')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Generate random EMP ID
        emp_id = f'EMP{random.randint(10000, 99999)}'
        
        # Check if first user, make them admin
        is_first = User.query.count() == 0
        role = 'admin' if is_first else 'employee'
        
        user = User(
            employee_id=emp_id,
            name=name,
            email=email,
            role=role,
            department_id=department_id if department_id else None,
            base_salary=0, # Default
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # To get user.id for LeaveBalance
        
        # Give default leave balance
        lb = LeaveBalance(employee_id=user.id, casual_leave=12, sick_leave=6, earned_leave=15)
        db.session.add(lb)
        
        # Audit log
        log = AuditLog(user_id=user.id, action='REGISTER', details=f'{user.name} registered as {role}', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', departments=departments)



@auth_bp.route('/logout')
@login_required
def logout():
    log = AuditLog(user_id=current_user.id, action='LOGOUT',
                   details=f'{current_user.name} logged out', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.address = request.form.get('address', current_user.address)
        new_pass = request.form.get('new_password')
        confirm_pass = request.form.get('confirm_password')
        if new_pass:
            if new_pass != confirm_pass:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('auth.profile'))
            if len(new_pass) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.set_password(new_pass)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', user=current_user)
