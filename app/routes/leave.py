from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from app import db
from app.models.leave import LeaveRequest, LeaveBalance

leave_bp = Blueprint('leave', __name__)


@leave_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if request.method == 'POST':
        f = request.form
        from_date = datetime.strptime(f['from_date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(f['to_date'], '%Y-%m-%d').date()
        
        if to_date < from_date:
            flash('End date cannot be before start date.', 'danger')
            return redirect(url_for('leave.apply'))
        
        # Calculate business days
        days = 0
        cur = from_date
        while cur <= to_date:
            if cur.weekday() < 5:
                days += 1
            cur += timedelta(days=1)
        
        if days == 0:
            flash('No working days in selected range.', 'danger')
            return redirect(url_for('leave.apply'))
        
        # Check balance
        lb = LeaveBalance.query.filter_by(employee_id=current_user.id).first()
        leave_type = f['leave_type']
        if lb and leave_type != 'unpaid':
            balance = getattr(lb, f'{leave_type}_leave', 0)
            if days > balance:
                flash(f'Insufficient {leave_type} leave balance. Available: {balance} days.', 'danger')
                return redirect(url_for('leave.apply'))
        
        # Check overlapping
        overlap = LeaveRequest.query.filter(
            LeaveRequest.employee_id == current_user.id,
            LeaveRequest.status.in_(['pending', 'approved']),
            LeaveRequest.from_date <= to_date,
            LeaveRequest.to_date >= from_date
        ).first()
        if overlap:
            flash('You already have a leave request overlapping this period.', 'danger')
            return redirect(url_for('leave.apply'))
        
        lr = LeaveRequest(
            employee_id=current_user.id,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            days=days,
            reason=f.get('reason', ''),
            status='pending'
        )
        db.session.add(lr)
        db.session.commit()
        flash(f'Leave request submitted for {days} day(s)!', 'success')
        return redirect(url_for('leave.history'))
    
    lb = LeaveBalance.query.filter_by(employee_id=current_user.id).first()
    return render_template('leave/apply.html', leave_bal=lb, today=date.today())


@leave_bp.route('/history')
@login_required
def history():
    if current_user.role in ('admin', 'hr'):
        leaves = LeaveRequest.query.order_by(LeaveRequest.applied_on.desc()).all()
    else:
        leaves = LeaveRequest.query.filter_by(employee_id=current_user.id).order_by(
            LeaveRequest.applied_on.desc()
        ).all()
    lb = LeaveBalance.query.filter_by(employee_id=current_user.id).first()
    return render_template('leave/history.html', leaves=leaves, leave_bal=lb)


@leave_bp.route('/<int:leave_id>/cancel', methods=['POST'])
@login_required
def cancel_leave(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    if leave.employee_id != current_user.id and current_user.role not in ('admin', 'hr'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('leave.history'))
    if leave.status not in ('pending',):
        flash('Only pending leaves can be cancelled.', 'warning')
        return redirect(url_for('leave.history'))
    leave.status = 'cancelled'
    db.session.commit()
    flash('Leave request cancelled.', 'info')
    return redirect(url_for('leave.history'))
