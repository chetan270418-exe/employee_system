# EmpTrack — Smart Employee Attendance & Payroll Management System

A modern, cloud-ready **Employee Attendance and Payroll Management System** built with **Flask**, **SQLAlchemy**, **MySQL**, and **Vanilla CSS/JS**. EmpTrack provides role-based access control for Admins, HR Managers, and Employees, incorporating multi-method attendance verification (QR Code, GPS), automated Indian tax regime payroll processing, leave management, document storage, and reporting.

---

## 🌟 Key Features

### 👤 1. Role-Based Dashboards
- **Admin**: Overall company overview, department management, employee administration, bulk payroll processing, system audit logs, and analytics.
- **HR**: Daily attendance management, manual check-in/check-out overrides, leave approval workflows, and HR reporting.
- **Employee**: Personal self-service portal to mark daily attendance (QR / GPS), apply for leaves, view leave balances, and download monthly PDF salary slips.

### ⏱️ 2. Smart Attendance Tracking
- **QR Code Scanning**: Admins generate a daily office QR code; employees scan via mobile/desktop camera to instantly mark check-in or check-out.
- **GPS Location Verification**: Validates employee location using browser Geolocation API before accepting attendance.
- **Manual Overrides & Overtime**: Tracks working hours, overtime, late check-ins, and half-days automatically.

### 💸 3. Automated Payroll & Tax Calculations
- **Indian Tax Regime (FY 2024-25)**: Calculates statutory deductions like Provident Fund (PF - 12%), ESI (0.75%), and TDS (Income Tax) based on current tax slabs.
- **Dynamic Salary Math**: Takes into account present days, working days, unpaid leaves, bonuses, and overtime.
- **Automated PDF Salary Slips**: Generates print-ready PDF salary slips powered by ReportLab.

### 🌴 4. Leave & Document Management
- **Leave Balances**: Tracks Casual, Sick, and Earned leaves in real time.
- **Document Management**: Allows uploading and secure viewing/downloading of employee documents (Resumes, Aadhaar, PAN, Offer Letters).

---

## 🏗️ Project Structure

```text
employee_system/
├── app/
│   ├── __init__.py           # Flask App Factory & extension initialization
│   ├── config.py             # Configuration classes (Development, Production, Database URIs)
│   ├── models/               # SQLAlchemy Models
│   │   ├── user.py           # User & Department models
│   │   ├── attendance.py     # Attendance model
│   │   ├── leave.py          # LeaveRequest & LeaveBalance models
│   │   ├── payroll.py        # Payroll model
│   │   └── document.py       # Document & AuditLog models
│   ├── routes/               # Blueprint controllers
│   │   ├── auth.py           # Authentication & Profile routes
│   │   ├── admin.py          # Admin Management routes
│   │   ├── hr.py             # HR Management routes
│   │   ├── employee.py       # Employee Self-Service routes
│   │   ├── attendance.py     # Attendance & QR Code routes
│   │   ├── leave.py          # Leave Management routes
│   │   ├── payroll.py        # Payroll Generation routes
│   │   ├── reports.py        # Analytics & Export routes
│   │   └── documents.py      # File Management routes
│   ├── services/             # Core Business Logic Services
│   │   ├── payroll_engine.py # Indian Payroll Math & Tax calculation engine
│   │   ├── pdf_generator.py  # ReportLab PDF Payslip generator
│   │   ├── qr_service.py     # Token generation & QR rendering engine
│   │   └── storage_service.py# Local/S3 file abstraction layer
│   ├── static/               # Static assets
│   │   ├── css/style.css     # Design System (Colors, Typography, Layouts)
│   │   └── js/main.js        # Dynamic UI logic, notifications & tooltips
│   └── templates/            # Jinja2 HTML Templates
│       ├── base.html         # Sidebar & Header base layout
│       ├── auth/             # Login & Registration templates
│       ├── admin/            # Admin dashboards & management templates
│       ├── hr/               # HR dashboard & approval templates
│       ├── employee/         # Employee dashboard & history templates
│       ├── attendance/       # Mark, QR Scan & QR Generate templates
│       ├── leave/            # Leave application & history templates
│       ├── payroll/          # Payroll index & detailed view templates
│       ├── reports/          # Reports hub & filterable reports
│       └── documents/        # File management templates
├── uploads/                  # Storage folder for uploaded employee documents
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── seed.py                   # Database table creator & demo data seeder
```

---

## 🛠️ Local Installation & Setup

### Prerequisites
- **Python 3.10+** installed.
- **MySQL Server** (or XAMPP/WAMP) running locally.

### Step 1: Clone or Navigate to Project Directory
```bash
cd d:/student/employee_system
```

### Step 2: Create & Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Update the `.env` file with your local MySQL credentials:
```env
SECRET_KEY=supersecretkey-change-in-production-2024
DATABASE_URL=mysql+pymysql://<DB_USER>:<DB_PASSWORD>@localhost/<DB_NAME>
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```
*(Note: If your password contains `@` or special characters, URL-encode them. E.g., `@` becomes `%40`)*

### Step 5: Initialize & Seed Database
Run the seed script to create all database tables and populate standard departments & demo users:
```bash
python seed.py
```

### Step 6: Start the Development Server
```bash
python run.py
```
Open your browser and navigate to **`http://localhost:5000`**.

---

## 👥 Demo User Accounts

If you ran `seed.py`, you can test the system using the following credentials:

| Role | Email | Password |
| :--- | :--- | :--- |
| **System Admin** | `admin@emptrack.com` | `Admin@123` |
| **HR Manager** | `hr@emptrack.com` | `Hr@123` |
| **Employee** | `emp@emptrack.com` | `Emp@123` |

---

## 🚀 Deployment Guide
For deploying to **AWS (EC2, RDS MySQL, S3 Bucket)**, please refer to the dedicated **[AWS_GUIDE.md](AWS_GUIDE.md)** document.
