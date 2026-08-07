"""
Payroll Engine — Calculates Indian salary structure
"""
import calendar
from decimal import Decimal
from datetime import date
from app import db
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest
from app.models.payroll import Payroll


STANDARD_WORK_HOURS = 8
OVERTIME_MULTIPLIER = Decimal('1.5')

# Indian statutory rates
PF_RATE = Decimal('0.12')       # 12% of basic
ESI_RATE = Decimal('0.0075')    # 0.75% of gross
TDS_SLAB = [
    (300000, Decimal('0')),
    (600000, Decimal('0.05')),
    (900000, Decimal('0.10')),
    (1200000, Decimal('0.15')),
    (1500000, Decimal('0.20')),
    (float('inf'), Decimal('0.30')),
]


def calculate_tds(annual_gross):
    """Calculate TDS based on Indian income tax slabs (new regime FY 2024-25)."""
    tax = Decimal('0')
    prev_slab = Decimal('0')
    annual = Decimal(str(annual_gross))
    for slab, rate in TDS_SLAB:
        slab_d = Decimal(str(slab))
        if annual <= prev_slab:
            break
        taxable = min(annual, slab_d) - prev_slab
        tax += taxable * rate
        prev_slab = slab_d
    # Standard deduction of 75000
    std_deduction = Decimal('75000')
    taxable_income = max(annual - std_deduction, Decimal('0'))
    # Recalculate with standard deduction
    tax = Decimal('0')
    prev_slab = Decimal('0')
    for slab, rate in TDS_SLAB:
        slab_d = Decimal(str(slab))
        if taxable_income <= prev_slab:
            break
        taxable = min(taxable_income, slab_d) - prev_slab
        tax += taxable * rate
        prev_slab = slab_d
    monthly_tds = tax / 12
    return monthly_tds.quantize(Decimal('0.01'))


def get_working_days(year, month):
    """Get total working days (Mon-Fri) in a month."""
    _, days_in_month = calendar.monthrange(year, month)
    working = 0
    for d in range(1, days_in_month + 1):
        weekday = date(year, month, d).weekday()
        if weekday < 5:  # Monday=0, Friday=4
            working += 1
    return working


def generate_payroll(employee, month, year, bonus=0, other_deductions=0, generated_by_id=None):
    """Generate payroll for an employee for a given month/year."""
    # Check if already exists
    existing = Payroll.query.filter_by(
        employee_id=employee.id, month=month, year=year
    ).first()
    if existing:
        return existing, 'exists'

    base = Decimal(str(employee.base_salary))
    working_days = get_working_days(year, month)

    # Count present days from attendance
    month_start = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    month_end = date(year, month, days_in_month)

    att_records = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date >= month_start,
        Attendance.date <= month_end,
        Attendance.status.in_(['present', 'late'])
    ).all()
    half_days = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date >= month_start,
        Attendance.date <= month_end,
        Attendance.status == 'half_day'
    ).count()

    present_days = Decimal(len(att_records)) + Decimal(half_days) * Decimal('0.5')

    # Count approved leave days
    approved_leaves = LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee.id,
        LeaveRequest.status == 'approved',
        LeaveRequest.from_date >= month_start,
        LeaveRequest.to_date <= month_end,
        LeaveRequest.leave_type.in_(['casual', 'sick', 'earned'])
    ).all()
    leave_days = Decimal(sum(lr.days for lr in approved_leaves))
    paid_days = present_days + leave_days
    absent_days = max(Decimal(working_days) - paid_days, Decimal('0'))

    # Per-day salary
    per_day = base / Decimal(working_days) if working_days > 0 else Decimal('0')

    # Leave deduction (unpaid only)
    unpaid_leaves = LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee.id,
        LeaveRequest.status == 'approved',
        LeaveRequest.from_date >= month_start,
        LeaveRequest.to_date <= month_end,
        LeaveRequest.leave_type == 'unpaid'
    ).all()
    unpaid_days = Decimal(sum(lr.days for lr in unpaid_leaves))
    leave_deduction = unpaid_days * per_day + absent_days * per_day

    # Allowances (% of base)
    hra = (base * Decimal('0.20')).quantize(Decimal('0.01'))
    da = (base * Decimal('0.10')).quantize(Decimal('0.01'))
    ta = Decimal('1500')  # Fixed travel allowance

    # Overtime
    overtime_records = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date >= month_start,
        Attendance.date <= month_end,
        Attendance.overtime_hours > 0
    ).all()
    total_overtime_hours = Decimal(sum(r.overtime_hours for r in overtime_records))
    hourly_rate = base / (Decimal(working_days) * Decimal(STANDARD_WORK_HOURS)) if working_days > 0 else Decimal('0')
    overtime_amount = (total_overtime_hours * hourly_rate * OVERTIME_MULTIPLIER).quantize(Decimal('0.01'))

    bonus_d = Decimal(str(bonus))
    gross = base + hra + da + ta + overtime_amount + bonus_d

    # Deductions
    pf = (base * PF_RATE).quantize(Decimal('0.01'))
    esi = (gross * ESI_RATE).quantize(Decimal('0.01')) if gross <= Decimal('21000') else Decimal('0')
    tds = calculate_tds(float(gross * 12))
    other_ded = Decimal(str(other_deductions))
    total_deductions = pf + esi + tds + leave_deduction + other_ded

    net = (gross - total_deductions).quantize(Decimal('0.01'))

    payroll = Payroll(
        employee_id=employee.id,
        month=month,
        year=year,
        working_days=working_days,
        present_days=float(present_days),
        absent_days=float(absent_days),
        leave_days=float(leave_days),
        base_salary=base,
        hra=hra,
        da=da,
        ta=ta,
        overtime_hours=float(total_overtime_hours),
        overtime_amount=overtime_amount,
        bonus=bonus_d,
        gross_salary=gross,
        pf=pf,
        esi=esi,
        tds=tds,
        leave_deduction=leave_deduction,
        other_deductions=other_ded,
        total_deductions=total_deductions,
        net_salary=net,
        generated_by=generated_by_id,
        status='generated'
    )
    db.session.add(payroll)
    db.session.commit()
    return payroll, 'created'
