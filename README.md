# Altrium PerformanceFlow — 20% Checkpoint

This is an early GitHub checkpoint of the Employee Performance Review Management System.

## Included
- Flask + SQLite project structure
- Role-based login/logout
- HR dashboard
- Employee directory
- Create employee profiles
- Assign supervisors
- Basic Supervisor My Team page
- Altrium corporate UI

## Intentionally excluded
The later Performance Blueprint, review cycle engine, activation snapshots, audit timelines, actions/notifications, self-assessment, peer review, supervisor evaluation, manager approval, PAR and PDP features are intentionally not included in this checkpoint.

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python init_db.py
python app.py
```

Open `http://127.0.0.1:5000`.

Demo HR: `hr@altrium.com` / `Admin123!`  
Demo Supervisor: `supervisor@altrium.com` / `Supervisor123!`

Do not commit `.venv/`, `database.db`, or secret files.
