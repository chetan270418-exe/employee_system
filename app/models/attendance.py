from app import db
from datetime import datetime


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    method = db.Column(db.Enum('qr', 'gps', 'manual', 'face'), default='manual')
    status = db.Column(db.Enum('present', 'absent', 'late', 'half_day', 'holiday', 'weekend'), default='present')
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    work_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('employee_id', 'date', name='unique_attendance'),)

    def __repr__(self):
        return f'<Attendance {self.employee_id} {self.date}>'
