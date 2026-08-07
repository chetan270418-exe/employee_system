from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from app import db
from app.models.attendance import Attendance
from app.services.qr_service import generate_attendance_qr, validate_qr_token

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/mark', methods=['GET'])
@login_required
def mark():
    today = date.today()
    existing = Attendance.query.filter_by(employee_id=current_user.id, date=today).first()
    return render_template('attendance/mark.html', today=today, existing=existing)


@attendance_bp.route('/qr-generate')
@login_required
def qr_generate():
    """Admin/HR generates QR code for today."""
    if current_user.role not in ('admin', 'hr'):
        flash('Access denied.', 'danger')
        return redirect(url_for('employee.dashboard'))
    qr_b64, qr_data, payload = generate_attendance_qr()
    return render_template('attendance/qr_generate.html', qr_b64=qr_b64, payload=payload)


@attendance_bp.route('/qr-scan', methods=['GET', 'POST'])
@login_required
def qr_scan():
    """Employee scans QR code to mark attendance."""
    if request.method == 'POST':
        qr_data = request.form.get('qr_data', '')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        valid, payload = validate_qr_token(qr_data)
        if not valid:
            return jsonify({'success': False, 'message': 'Invalid or expired QR code!'})
        
        today = date.today()
        now = datetime.now().time()
        existing = Attendance.query.filter_by(employee_id=current_user.id, date=today).first()
        
        if existing and existing.check_out:
            return jsonify({'success': False, 'message': 'You have already checked out today!'})
        
        if existing:
            # Check-out
            existing.check_out = now
            if existing.check_in:
                delta = datetime.combine(today, now) - datetime.combine(today, existing.check_in)
                existing.work_hours = round(delta.total_seconds() / 3600, 2)
                if existing.work_hours > 9:
                    existing.overtime_hours = round(existing.work_hours - 9, 2)
            db.session.commit()
            return jsonify({'success': True, 'message': f'Check-out recorded at {now.strftime("%H:%M")}!', 'action': 'checkout'})
        else:
            # Check-in
            # Determine if late (after 9:30 AM)
            cutoff = datetime.strptime('09:30', '%H:%M').time()
            status = 'late' if now > cutoff else 'present'
            att = Attendance(
                employee_id=current_user.id,
                date=today,
                check_in=now,
                method='qr',
                status=status,
                location_lat=float(lat) if lat else None,
                location_lng=float(lng) if lng else None,
            )
            db.session.add(att)
            db.session.commit()
            msg = f'Check-in recorded at {now.strftime("%H:%M")}'
            if status == 'late':
                msg += ' (marked as Late)'
            return jsonify({'success': True, 'message': msg, 'action': 'checkin'})
    
    today = date.today()
    existing = Attendance.query.filter_by(employee_id=current_user.id, date=today).first()
    return render_template('attendance/qr_scan.html', today=today, existing=existing)


@attendance_bp.route('/gps-checkin', methods=['POST'])
@login_required
def gps_checkin():
    """GPS-based check-in/out."""
    lat = request.json.get('lat')
    lng = request.json.get('lng')
    
    # Office location (update these coordinates)
    OFFICE_LAT = 28.6139  # Example: New Delhi
    OFFICE_LNG = 77.2090
    RADIUS_KM = 0.5  # 500 meters

    # Calculate distance
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth radius in km
    lat1, lon1 = radians(OFFICE_LAT), radians(OFFICE_LNG)
    lat2, lon2 = radians(float(lat)), radians(float(lng))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance = R * 2 * atan2(sqrt(a), sqrt(1-a))

    if distance > RADIUS_KM:
        return jsonify({'success': False, 'message': f'You are {distance:.2f} km away from office. GPS attendance requires you to be within {RADIUS_KM} km.'})

    today = date.today()
    now = datetime.now().time()
    existing = Attendance.query.filter_by(employee_id=current_user.id, date=today).first()
    
    if existing and existing.check_out:
        return jsonify({'success': False, 'message': 'Already checked out today!'})
    if existing:
        existing.check_out = now
        if existing.check_in:
            delta = datetime.combine(today, now) - datetime.combine(today, existing.check_in)
            existing.work_hours = round(delta.total_seconds() / 3600, 2)
            if existing.work_hours > 9:
                existing.overtime_hours = round(existing.work_hours - 9, 2)
        db.session.commit()
        return jsonify({'success': True, 'message': f'GPS Check-out at {now.strftime("%H:%M")}', 'action': 'checkout'})
    else:
        cutoff = datetime.strptime('09:30', '%H:%M').time()
        status = 'late' if now > cutoff else 'present'
        att = Attendance(
            employee_id=current_user.id, date=today,
            check_in=now, method='gps', status=status,
            location_lat=float(lat), location_lng=float(lng)
        )
        db.session.add(att)
        db.session.commit()
        return jsonify({'success': True, 'message': f'GPS Check-in at {now.strftime("%H:%M")}', 'action': 'checkin'})
