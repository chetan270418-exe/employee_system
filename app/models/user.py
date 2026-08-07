from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import login_manager


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employees = db.relationship('User', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'hr', 'employee'), default='employee', nullable=False)
    
    # Personal Info
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other'))
    profile_photo = db.Column(db.String(255))
    
    # Job Info
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    designation = db.Column(db.String(100))
    join_date = db.Column(db.Date, default=datetime.utcnow)
    employment_type = db.Column(db.Enum('full_time', 'part_time', 'contract'), default='full_time')
    
    # Salary
    base_salary = db.Column(db.Numeric(12, 2), default=0)
    
    # Bank & Tax
    bank_account = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    pan_number = db.Column(db.String(20))
    aadhaar_number = db.Column(db.String(20))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True, foreign_keys='Attendance.employee_id')
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True, foreign_keys='LeaveRequest.employee_id')
    payroll_records = db.relationship('Payroll', backref='employee', lazy=True, foreign_keys='Payroll.employee_id')
    documents = db.relationship('Document', backref='employee', lazy=True, foreign_keys='Document.employee_id')
    leave_balance = db.relationship('LeaveBalance', backref='employee', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
