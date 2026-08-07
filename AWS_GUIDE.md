# AWS Console Setup & Deployment Guide

This step-by-step guide walks you through setting up **AWS RDS (MySQL)**, **AWS S3 (Document/Image Storage)**, **AWS EC2 (Virtual Machine Host)**, uploading your application files, and configuring security groups through the **AWS Management Console**.

---

## 📋 Architecture Overview

```text
               +-------------------------------------------------------+
               |                  AWS Cloud                            |
               |                                                       |
  User ------> |   [ EC2 Host (Ubuntu / Nginx + Gunicorn) ]            |
               |        |                              |               |
               |        v                              v               |
               |   [ RDS MySQL Database ]       [ S3 Bucket Storage ]  |
               |   (EmpTrack DB Data)           (Documents & Payslips) |
               +-------------------------------------------------------+
```

---

## Step 1: Create AWS RDS (MySQL Database)

1. **Log in** to the [AWS Management Console](https://console.aws.amazon.com/).
2. Search for **RDS** in the top search bar and click on **RDS**.
3. In the RDS Dashboard, click **Create database**.
4. Choose **Standard create**.
5. Engine options:
   - Select **MySQL**.
   - Edition: **MySQL Community**.
   - Version: Select the latest version (e.g., MySQL 8.0.x).
6. Templates: Choose **Free tier** (or **Dev/Test**).
7. Settings:
   - **DB instance identifier**: `emptrack-db-instance`
   - **Master username**: `admin` (or your choice)
   - **Master password**: Enter a strong password (e.g., `Chetan@27`).
8. Instance configuration:
   - Select **db.t3.micro** or **db.t4g.micro** (Free tier eligible).
9. Connectivity:
   - **Public access**: Choose **Yes** (if connecting directly from local machine) or **No** (if accessing only within VPC from EC2).
   - **VPC security group**: Choose **Create new** and name it `emptrack-rds-sg`.
10. Additional configuration:
    - **Initial database name**: `employee_db`
11. Click **Create database**.
12. Once created, click on `emptrack-db-instance` and copy the **Endpoint URL** (e.g., `emptrack-db-instance.xxxxxx.us-east-1.rds.amazonaws.com`).

---

## Step 2: Create AWS S3 Bucket (Document & Asset Storage)

1. Search for **S3** in the AWS Console search bar and select **S3**.
2. Click **Create bucket**.
3. Bucket Details:
   - **Bucket name**: `emptrack-storage-bucket-2024` (must be globally unique).
   - **AWS Region**: Choose your preferred region (e.g., `us-east-1` or `ap-south-1`).
4. Block Public Access settings:
   - For public assets (e.g. employee avatars), uncheck **Block *all* public access** and acknowledge the prompt, OR keep it blocked and use AWS IAM access keys with Pre-Signed URLs.
5. Bucket Versioning: Keep disabled (or enable if version control for payslips is needed).
6. Click **Create bucket**.

---

## Step 3: Launch AWS EC2 Instance (Host Server)

1. Search for **EC2** in the AWS Console search bar and select **EC2**.
2. Click **Launch instance**.
3. Name and tags:
   - **Name**: `EmpTrack-Server`
4. Application and OS Images (AMI):
   - Choose **Ubuntu** (Ubuntu Server 22.04 LTS or 24.04 LTS, 64-bit Architecture).
5. Instance type:
   - Select **t2.micro** or **t3.micro** (Free tier eligible).
6. Key pair (login):
   - Click **Create new key pair**.
   - **Key pair name**: `emptrack-key`
   - **Key pair type**: `RSA`
   - **Private key file format**: `.pem` (for OpenSSH / Linux / macOS / PowerShell) or `.ppk` (for PuTTY).
   - Click **Create key pair** and save the downloaded file securely on your computer.
7. Network settings:
   - Click **Edit**.
   - Auto-assign public IP: **Enable**.
   - Select **Create security group**. Name: `emptrack-ec2-sg`.
   - Add the following **Inbound Security Group Rules**:

| Type | Protocol | Port Range | Source | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **SSH** | TCP | 22 | My IP (or Anywhere 0.0.0.0/0) | Remote Terminal Access |
| **HTTP** | TCP | 80 | Anywhere (0.0.0.0/0) | Public Web Access |
| **Custom TCP** | TCP | 5000 | Anywhere (0.0.0.0/0) | Direct Flask Port |

8. Configure storage: 8 GB General Purpose SSD (gp3).
9. Click **Launch instance**.
10. Go to EC2 Instances list, select `EmpTrack-Server`, and copy its **Public IPv4 Address** (e.g., `54.210.10.50`).

---

## Step 4: Configure Security Groups (Database & Host Access)

1. In EC2 Console, go to **Security Groups** under **Network & Security**.
2. Find `emptrack-rds-sg` (your RDS security group).
3. Select **Edit inbound rules** -> Click **Add rule**:
   - **Type**: MYSQL/Aurora (Port 3306)
   - **Source**: Select **Custom** and search/select `emptrack-ec2-sg` (allows EC2 instance to talk to RDS).
   - *(Optional)* Add another rule with your **My IP** to allow connecting from your local machine (e.g., MySQL Workbench).
4. Click **Save rules**.

---

## Step 5: Upload Files to EC2 Instance

There are two primary ways to upload application files from your computer to your EC2 instance:

### Option A: Uploading via SCP (Secure Copy Protocol)

Open PowerShell / Terminal on your local machine in the `d:\student\employee_system` directory:

```powershell
# 1. Set permission on your downloaded key (Linux/macOS only: chmod 400 emptrack-key.pem)

# 2. Compress your project directory (excluding venv)
Compress-Archive -Path * -DestinationPath employee_system.zip

# 3. Upload zip file to your EC2 instance
scp -i "C:\path\to\emptrack-key.pem" employee_system.zip ubuntu@<YOUR_EC2_PUBLIC_IP>:~/
```

### Option B: Uploading via Git / GitHub (Recommended)

1. Push your project code to a private GitHub repository.
2. Connect to EC2 via SSH and clone:
   ```bash
   git clone https://github.com/your-username/employee_system.git
   ```

---

## Step 6: Server Setup & Application Deployment on EC2

Connect to your EC2 instance using SSH:
```bash
ssh -i "C:\path\to\emptrack-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
```

Once connected to the EC2 terminal, execute the following steps:

### 1. Update Server & Install System Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx unzip -y
```

### 2. Unpack & Setup Application Directory
```bash
mkdir -p ~/employee_system
unzip employee_system.zip -d ~/employee_system
cd ~/employee_system
```

### 3. Create Virtual Environment & Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn cryptography
```

### 4. Configure `.env` File for AWS Environment
Create or edit `.env`:
```bash
nano .env
```
Paste your production settings (using your RDS Endpoint & S3 Bucket):
```env
SECRET_KEY=your-production-super-secret-key-2024
DATABASE_URL=mysql+pymysql://admin:Chetan%4027@emptrack-db-instance.xxxxxx.us-east-1.rds.amazonaws.com/employee_db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### 5. Seed Database on RDS
```bash
python3 seed.py
```

### 6. Configure Systemd Service for Gunicorn
Create a background service file to keep Flask running continuously:
```bash
sudo nano /etc/systemd/system/emptrack.service
```
Add the following content:
```ini
[Unit]
Description=Gunicorn instance to serve EmpTrack Flask App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/employee_system
Environment="PATH=/home/ubuntu/employee_system/venv/bin"
ExecStart=/home/ubuntu/employee_system/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start emptrack
sudo systemctl enable emptrack
```

### 7. Configure Nginx Reverse Proxy
```bash
sudo nano /etc/nginx/sites-available/emptrack
```
Add the following configuration:
```nginx
server {
    listen 80;
    server_name <YOUR_EC2_PUBLIC_IP>;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/emptrack /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🎯 Verification

Open your web browser and visit `http://<YOUR_EC2_PUBLIC_IP>`. Your **Cloud-Based Smart Employee Attendance & Payroll Management System** is now live on AWS!
