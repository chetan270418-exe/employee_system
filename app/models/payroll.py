from app import db
from datetime import datetime


class Payroll(db.Model):
    __tablename__ = 'payrolls'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    
    # Working info
    working_days = db.Column(db.Integer, default=0)
    present_days = db.Column(db.Float, default=0)
    absent_days = db.Column(db.Float, default=0)
    leave_days = db.Column(db.Float, default=0)
    
    # Earnings
    base_salary = db.Column(db.Numeric(12, 2), default=0)
    hra = db.Column(db.Numeric(12, 2), default=0)          # House Rent Allowance
    da = db.Column(db.Numeric(12, 2), default=0)           # Dearness Allowance
    ta = db.Column(db.Numeric(12, 2), default=0)           # Travel Allowance
    overtime_hours = db.Column(db.Float, default=0)
    overtime_amount = db.Column(db.Numeric(12, 2), default=0)
    bonus = db.Column(db.Numeric(12, 2), default=0)
    gross_salary = db.Column(db.Numeric(12, 2), default=0)
    
    # Deductions
    pf = db.Column(db.Numeric(12, 2), default=0)           # Provident Fund
    esi = db.Column(db.Numeric(12, 2), default=0)          # Employee State Insurance
    tds = db.Column(db.Numeric(12, 2), default=0)          # Tax Deducted at Source
    leave_deduction = db.Column(db.Numeric(12, 2), default=0)
    other_deductions = db.Column(db.Numeric(12, 2), default=0)
    total_deductions = db.Column(db.Numeric(12, 2), default=0)
    
    # Net
    net_salary = db.Column(db.Numeric(12, 2), default=0)
    
    # Status & Meta
    status = db.Column(db.Enum('draft', 'generated', 'paid'), default='generated')
    slip_path = db.Column(db.String(255))
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    generated_on = db.Column(db.DateTime, default=datetime.utcnow)
    paid_on = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('employee_id', 'month', 'year', name='unique_payroll'),)

    def __repr__(self):
        return f'<Payroll {self.employee_id} {self.month}/{self.year}>'
