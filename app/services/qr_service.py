"""
QR Code Service — Generates attendance QR codes
"""
import qrcode
import os
import json
import hashlib
from datetime import date
from io import BytesIO
import base64


def generate_attendance_qr(office_id='MAIN', office_name='Head Office', secret='payroll2024'):
    """Generate a time-based QR code for attendance marking."""
    today = str(date.today())
    payload = {
        'office_id': office_id,
        'office_name': office_name,
        'date': today,
        'token': hashlib.sha256(f'{office_id}{today}{secret}'.encode()).hexdigest()[:16]
    }
    qr_data = json.dumps(payload)
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#1a237e', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    return img_b64, qr_data, payload


def validate_qr_token(qr_data_str, secret='payroll2024'):
    """Validate a scanned QR code token."""
    try:
        payload = json.loads(qr_data_str)
        today = str(date.today())
        expected_token = hashlib.sha256(f"{payload['office_id']}{today}{secret}".encode()).hexdigest()[:16]
        if payload.get('token') == expected_token and payload.get('date') == today:
            return True, payload
        return False, None
    except Exception:
        return False, None
