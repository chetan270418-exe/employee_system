# 🏢 EmpTrack — Smart Employee Attendance & Payroll Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/Database-MySQL%208.0-orange.svg)](https://www.mysql.com/)
[![AWS Ready](https://img.shields.io/badge/Cloud-AWS%20EC2%20%7C%20RDS%20%7C%20S3-FF9900.svg)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

An enterprise-ready, cloud-deployable **Employee Attendance and Payroll Management System** built with **Python (Flask)**, **SQLAlchemy ORM**, **MySQL**, and a responsive modern CSS design system. 

EmpTrack automates the complete lifecycle of human resource operations: multi-modal attendance verification (QR Code & GPS coordinates), automated Indian statutory payroll processing (PF, ESI, TDS), dynamic leave approvals, document archiving, and PDF salary slip generation.

---

## 📑 Table of Contents
- [🌟 Key Features](#-key-features)
- [📋 System Architecture](#-system-architecture)
- [⚙️ Prerequisites](#️-prerequisites)
- [🚀 Step-by-Step Local Setup Guide](#-step-by-step-local-setup-guide)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create and Activate Virtual Environment](#2-create-and-activate-virtual-environment)
  - [3. Install Required Dependencies](#3-install-required-dependencies)
  - [4. Configure Secrets & Environment Variables (.env)](#4-configure-secrets--environment-variables-env)
  - [5. Setup the MySQL Database & Seed Data](#5-setup-the-mysql-database--seed-data)
  - [6. Start the Web Server](#6-start-the-web-server)
- [🔑 Demo Login Credentials](#-demo-login-credentials)
- [🧰 How to Manage Secret Keys & Passwords](#-how-to-manage-secret-keys--passwords)
- [📂 Project Directory Structure](#-project-directory-structure)
- [🛠️ Troubleshooting & FAQ](#️-troubleshooting--faq)
- [☁️ AWS Cloud Deployment](#️-aws-cloud-deployment)

---

## 🌟 Key Features

### 1. 👥 Role-Based Portals & Dashboards
- **System Admin**: Comprehensive company metrics, department creation, employee lifecycle management, bulk monthly payroll execution, and tamper-evident audit logs.
- **HR Manager**: Real-time attendance ledger, manual check-in/out adjustments, and multi-state leave approval workflow.
- **Employee Self-Service**: Check-in portal, personal attendance histories, leave balance tracking, document uploads, and PDF salary slip downloads.

### 2. 📍 Smart Attendance Tracking
- **Office QR Code Scanner**: Admins generate daily rotating QR tokens; employees scan from their device camera to check in/out with anti-proxy verification.
- **GPS Location Verification**: Validates browser Geolocation coordinates within office perimeter radius.
- **Automatic Calculation**: Tracks standard hours, overtime, tardiness, and half-days.

### 3. 💰 Automated Indian Payroll & Tax Engine
- **Statutory Deductions (FY 2024-25)**:
  - **Provident Fund (PF)**: 12% of basic salary.
  - **Employee State Insurance (ESI)**: 0.75% of gross earnings (for eligible slabs).
  - **Income Tax (TDS)**: Real-time calculation according to Indian income tax slabs.
  - **Allowances**: HRA (20%), DA (10%), Travel Allowance (TA), and Overtime multipliers.
- **PDF Salary Slip Generator**: Generates print-ready salary slips automatically formatted using ReportLab.

### 4. 📁 Document & Leave Management
- **Leave Balances**: Tracks Casual Leave (12), Sick Leave (6), and Earned Leave (15) with automatic balance deduction upon approval.
- **Document Management**: Upload and download resumes, identity proofs (PAN, Aadhaar), and contracts.

---

## 📋 System Architecture

```text
               +-------------------------------------------------------+
               |                    Web Browser                        |
               |          (Admin / HR / Employee Portals)              |
               +---------------------------+---------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               |                Flask Application Server               |
               |                                                       |
               |  - Auth & Role Guards        - QR / GPS Verification  |
               |  - Leave Engine              - Indian Payroll Math    |
               |  - ReportLab PDF Engine      - Document Storage       |
               +-------------+-----------------------------+-----------+
                             |                             |
                             v                             v
               +---------------------------+ +-------------------------+
               |     MySQL / AWS RDS       | |     Uploads / AWS S3    |
               |  (Users, Records, Logs)   | |  (Payslips, Documents)  |
               +---------------------------+ +-------------------------+
```

---

## ⚙️ Prerequisites

Make sure the following software is installed on your operating system:

1. **Python 3.10 or higher**: [Download Python](https://www.python.org/downloads/) (Check with `python --version`)
2. **Git**: [Download Git](https://git-scm.com/) (Check with `git --version`)
3. **MySQL Server** (Choose one):
   - Standalone **MySQL Community Server 8.0+** & MySQL Workbench: [Download MySQL](https://dev.mysql.com/downloads/installer/)
   - OR **XAMPP / WAMP** with MySQL/MariaDB service running.

---

## 🚀 Step-by-Step Local Setup Guide

Follow these exact steps to run the application on your computer:

### 1. Clone the Repository

Open your terminal (PowerShell, Command Prompt, or Bash) and clone the repository:

```bash
git clone https://github.com/chetan270418-exe/employee_system.git
cd employee_system
```

---

### 2. Create and Activate Virtual Environment

Isolate application dependencies by creating a Python virtual environment:

- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If PowerShell gives an execution policy error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

Once activated, your terminal prompt will display `(venv)`.

---

### 3. Install Required Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. Configure Secrets & Environment Variables (.env)

The repository provides a template file named `.env.example`. Copy it to create your private `.env` file:

- **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
- **Linux / macOS:**
  ```bash
  cp .env.example .env
  ```

Open `.env` in any text editor (VS Code, Notepad, Nano) and update the database configuration:

```env
SECRET_KEY=supersecretkey-change-in-production-2024
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/employee_db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

> ⚠️ **IMPORTANT (Special Characters in Password):**  
> If your MySQL password contains special characters such as `@`, `:`, `/`, or `?`, you **must URL-encode** them in the connection string:
> - `@` becomes `%40` (Example: `Chetan@27` ➡️ `Chetan%4027`)
> - `#` becomes `%23`
> - `&` becomes `%26`
> 
> *Example connection string:*
> ```text
> DATABASE_URL=mysql+pymysql://root:Chetan%4027@localhost:3306/employee_db
> ```

---

### 5. Setup the MySQL Database & Seed Data

#### A. Create the Database
Ensure your MySQL service is running, then create the database named `employee_db`:

- **Using MySQL CLI:**
  ```sql
  CREATE DATABASE IF NOT EXISTS employee_db;
  ```
- **Or Using MySQL Workbench / phpMyAdmin:**
  Create a new schema named `employee_db` with default collation (`utf8mb4`).

#### B. Seed Default Departments, Users & Test Data
Run the built-in database initialization script:

```bash
python seed.py
```

This will automatically create all tables and populate sample employees, roles, past attendance records, and leave balances!

---

### 6. Start the Web Server

Launch the Flask development server:

```bash
python run.py
```

Open your web browser and navigate to:
👉 **`http://localhost:5000`** (or `http://127.0.0.1:5000`)

---

## 🔑 Demo Login Credentials

You can test each user role immediately using these seeded accounts:

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@emptrack.com` | `Admin@123` | Complete administration, departments, bulk payroll, audit logs |
| **HR Manager** | `hr@emptrack.com` | `Hr@123` | Attendance ledger, QR generation, leave approvals |
| **Employee** | `emp@emptrack.com` | `Emp@123` | Daily attendance check-in, leave apply, PDF salary slip download |

> 💡 **Self-Registration:** New employees can also click **"Create Account"** directly on the login page to register.

---

## 🧰 How to Manage Secret Keys & Passwords

### 1. Generating a Secure `SECRET_KEY`
In production, do not use simple secret strings. Generate a cryptographically secure random key using Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste it as `SECRET_KEY` in your `.env` file:
```env
SECRET_KEY=9f82ab73b18d24950e18df73cb9110d7a04917482937cdb84f291048bc821094
```

### 2. Protecting Sensitive Data
- The `.gitignore` file is already configured to ignore `.env`, `venv/`, `uploads/`, and Python cache files.
- **Never commit your `.env` file to GitHub.** Always share configuration structure via `.env.example`.

---

## 📂 Project Directory Structure

```text
employee_system/
├── app/
│   ├── __init__.py           # Flask App Factory & Blueprint registration
│   ├── config.py             # Config loading from .env
│   ├── models/               # SQLAlchemy Models
│   │   ├── user.py           # User and Department models
│   │   ├── attendance.py     # Attendance check-in/out records
│   │   ├── leave.py          # Leave requests & balances
│   │   ├── payroll.py        # Monthly payroll records
│   │   └── document.py       # Documents & Audit trail logs
│   ├── routes/               # Blueprint Route Handlers
│   │   ├── auth.py           # Login, registration, profile & logout
│   │   ├── admin.py          # Admin dashboard & employee CRUD
│   │   ├── hr.py             # HR dashboard, attendance & leave approvals
│   │   ├── employee.py       # Employee dashboard & records
│   │   ├── attendance.py     # QR scanner & GPS check-in endpoints
│   │   ├── leave.py          # Leave application & tracking
│   │   ├── payroll.py        # Payroll generation & payslip download
│   │   ├── reports.py        # Excel & summary reporting
│   │   └── documents.py      # File uploads & downloads
│   ├── services/             # Core Business Logic
│   │   ├── payroll_engine.py # Indian tax regime calculations (PF, ESI, TDS)
│   │   ├── pdf_generator.py  # ReportLab salary slip generator
│   │   ├── qr_service.py     # Time-based QR token generation
│   │   └── storage_service.py# Local & S3 storage abstraction
│   ├── static/               # Assets (CSS styles, JavaScript, Images)
│   └── templates/            # Jinja2 HTML templates
├── uploads/                  # Local folder for uploaded documents & slips
├── .env.example              # Sample environment template for clones
├── .gitignore                # Git ignore rules (keeps secrets safe)
├── AWS_GUIDE.md              # Full AWS EC2 + RDS + S3 deployment manual
├── README.md                 # Project documentation & local setup guide
├── requirements.txt          # Python dependencies
├── run.py                    # Server startup script
└── seed.py                   # Database schema & demo seed script
```

---

## 🛠️ Troubleshooting & FAQ

### 1. `pymysql.err.OperationalError: (1045, "Access denied for user 'root'@'localhost'")`
- **Cause**: The password specified in `DATABASE_URL` is incorrect or unencoded.
- **Fix**: Open `.env` and verify your MySQL password. If your password contains `@`, encode it as `%40` (e.g., `Pass@123` ➡️ `Pass%40123`).

### 2. `RuntimeError: 'cryptography' package is required for sha256_password`
- **Cause**: MySQL 8.0+ uses `caching_sha2_password` by default, which requires Python's cryptography package.
- **Fix**: Ensure `cryptography` is installed:
  ```bash
  pip install cryptography
  ```

### 3. `Can't connect to MySQL server on 'localhost' (10061)`
- **Cause**: MySQL service is not started.
- **Fix**:
  - **Windows Services**: Open `services.msc`, locate `MySQL80` (or `MySQL`), and click **Start**.
  - **XAMPP**: Open XAMPP Control Panel and start the **MySQL** module.

### 4. `Address already in use (Port 5000)`
- **Cause**: Another application or Flask instance is already using port 5000.
- **Fix**: Edit `run.py` to specify a different port (e.g., `port=5050`) or terminate the existing process.

---

## ☁️ AWS Cloud Deployment

Ready to take your project from localhost to the cloud?  
Check out our comprehensive **[AWS_GUIDE.md](AWS_GUIDE.md)** for a complete step-by-step console guide covering:
- Setting up an **AWS RDS MySQL** database.
- Creating an **AWS S3 Bucket** for file & payslip storage.
- Provisioning an **AWS EC2 Ubuntu Instance**.
- Configuring **Security Groups** (HTTP, SSH, MySQL).
- Deploying with **Gunicorn** (Systemd service) and **Nginx Reverse Proxy**.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
