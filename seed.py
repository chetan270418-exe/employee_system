"""
Seed script — Creates DB tables and inserts demo data
Run: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User, Department
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest, LeaveBalance
from app.models.payroll import Payroll
from app.models.document import Document, AuditLog
from datetime import date, timedelta
import random


def seed():
    app = create_app()
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created!")

        # Check if already seeded
        if User.query.first():
            print("Database already has data. Skipping seed.")
            return

        # ─── Departments ────────────────────────────────────────────
        dept_names = ['Engineering', 'Human Resources', 'Finance', 'Marketing', 'Operations']
        depts = []
        for name in dept_names:
            d = Department(name=name, description=f'{name} department')
            db.session.add(d)
            depts.append(d)
        db.session.flush()

        # ─── Admin ──────────────────────────────────────────────────
        admin = User(
            employee_id='EMP0001',
            name='Admin User',
            email='admin@emptrack.com',
            role='admin',
            department_id=depts[0].id,
            designation='System Administrator',
            base_salary=80000,
            phone='9876543210',
            join_date=date(2022, 1, 1),
            pan_number='ABCDE1234F',
            bank_account='1234567890',
            bank_name='SBI'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

        # ─── HR ─────────────────────────────────────────────────────
        hr = User(
            employee_id='EMP0002',
            name='Priya Sharma',
            email='hr@emptrack.com',
            role='hr',
            department_id=depts[1].id,
            designation='HR Manager',
            base_salary=60000,
            phone='9876543211',
            join_date=date(2022, 3, 15),
            pan_number='BCDEF2345G',
            bank_account='2345678901',
            bank_name='HDFC'
        )
        hr.set_password('Hr@123')
        db.session.add(hr)

        # ─── Employees ───────────────────────────────────────────────
        emp_data = [
            ('Rahul Verma', 'emp@emptrack.com', 'Emp@123', depts[0], 'Software Engineer', 55000),
            ('Sunita Patel', 'sunita@emptrack.com', 'Welcome@123', depts[2], 'Accountant', 45000),
            ('Amit Kumar', 'amit@emptrack.com', 'Welcome@123', depts[3], 'Marketing Lead', 50000),
            ('Neha Singh', 'neha@emptrack.com', 'Welcome@123', depts[0], 'Senior Developer', 70000),
            ('Vikram Joshi', 'vikram@emptrack.com', 'Welcome@123', depts[4], 'Operations Manager', 65000),
        ]
        employees = []
        for i, (name, email, pwd, dept, desig, salary) in enumerate(emp_data):
            emp = User(
                employee_id=f'EMP{str(i+3).zfill(4)}',
                name=name,
                email=email,
                role='employee',
                department_id=dept.id,
                designation=desig,
                base_salary=salary,
                phone=f'98765432{i+12}',
                join_date=date(2023, random.randint(1, 6), random.randint(1, 28)),
                pan_number=f'CDEFG{i}345H',
                bank_account=f'{i+3}456789012',
                bank_name=random.choice(['SBI', 'HDFC', 'ICICI', 'Axis'])
            )
            emp.set_password(pwd)
            db.session.add(emp)
            employees.append(emp)
        db.session.flush()

        # ─── Leave Balances ─────────────────────────────────────────
        all_users = [admin, hr] + employees
        for u in all_users:
            lb = LeaveBalance(employee_id=u.id, casual_leave=12, sick_leave=6, earned_leave=15)
            db.session.add(lb)
        db.session.flush()

        # ─── Attendance (last 30 days for employees) ─────────────────
        today = date.today()
        for emp in employees:
            for i in range(30, 0, -1):
                d = today - timedelta(days=i)
                if d.weekday() >= 5:  # Skip weekends
                    continue
                rand = random.random()
                if rand < 0.05:
                    status = 'absent'
                    check_in, check_out, work_hrs, ot = None, None, 0, 0
                elif rand < 0.15:
                    status = 'late'
                    check_in = __import__('datetime').time(10, random.randint(5, 45))
                    check_out = __import__('datetime').time(19, 0)
                    work_hrs = 8.5
                    ot = 0
                else:
                    status = 'present'
                    check_in = __import__('datetime').time(9, random.randint(0, 29))
                    check_out_h = random.choice([18, 19, 20])
                    check_out = __import__('datetime').time(check_out_h, random.randint(0, 59))
                    work_hrs = check_out_h - 9
                    ot = max(0, work_hrs - 9)

                att = Attendance(
                    employee_id=emp.id,
                    date=d,
                    check_in=check_in,
                    check_out=check_out,
                    status=status,
                    method=random.choice(['qr', 'gps', 'manual']),
                    work_hours=work_hrs,
                    overtime_hours=ot
                )
                db.session.add(att)

        # ─── Sample Leave Requests ────────────────────────────────────
        for emp in employees[:3]:
            lr = LeaveRequest(
                employee_id=emp.id,
                leave_type='casual',
                from_date=today + timedelta(days=3),
                to_date=today + timedelta(days=4),
                days=2,
                reason='Personal work',
                status='pending'
            )
            db.session.add(lr)

        db.session.commit()
        print("✅ Database seeded successfully!")
        print("\nDemo Login Credentials:")
        print("  Admin: admin@emptrack.com / Admin@123")
        print("  HR:    hr@emptrack.com / Hr@123")
        print("  Emp:   emp@emptrack.com / Emp@123")
        print("\nRun: python run.py")


if __name__ == '__main__':
    seed()
