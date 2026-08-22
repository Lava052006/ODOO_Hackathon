# ARIA — Workday Command Centre & HR Management System

ARIA is a modern, unified Human Resource Management & Workday Command Centre system built with a **Vue 3** frontend and a **Django REST + PostgreSQL** backend.

---

## Quick Start (One-Click Setup)

Run the automated startup assistant script from the project root:

```bash
python start.py
```

### What `start.py` does automatically:
1. **PostgreSQL Check**: Detects or starts local PostgreSQL (`pgdata` cluster) on port 5432.
2. **Virtual Environment**: Sets up `backend/.venv` and installs dependencies from `backend/requirements.txt`.
3. **Database Schema & Seeding**: Creates `aria_db`, runs all migrations, and automatically seeds 120 employees, 7-day attendance logs, weekly roster shifts, salary structures, and leaves if unseeded.
4. **Frontend Setup**: Installs Node packages via `pnpm` or `npm`.
5. **Live Servers**: Concurrently runs the Django API (`http://127.0.0.1:8000/api/`) and the Vue Frontend (`http://localhost:5173/`).

---

## Manual Startup (Alternative)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver 127.0.0.1:8000
```

### 2. Frontend Setup
```bash
cd frontend
pnpm install
pnpm run dev
```

---

## Demo Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **HR Administrator** | `admin@aria.com` | `Aria@2026` |
| **Employee Self-Service** | `employee@aria.com` | `Aria@2026` |

---

## Architecture & Features

- **Command Centre**: Real-time operational alignment, 7-day attendance signals, and pending approval queue.
- **People**: Directory of 120 employees across 6 departments with live presence indicators.
- **Attendance**: Real-time check-in/out tracker, exception management, and CSV export.
- **Time Off**: Decision queue, capacity protections, and dynamic team away calendar.
- **Payroll**: Pre-flight validation checks, salary structures, readiness gauge, and payslip generation.
- **Roster**: Weekly shift matrix, department coverage analytics, and roster publishing.
