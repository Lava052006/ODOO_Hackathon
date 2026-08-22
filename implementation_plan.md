# Implementation Plan: PostgreSQL Backend & Full-Stack Integration for ARIA

ARIA is a Workday Command Centre & HR Management System. This plan outlines building a robust Django REST backend powered by PostgreSQL, implementing data models, authentication, attendance, leave management, payroll, roster planning, and real-time feeds, and connecting the Vue frontend seamlessly while eliminating all mock data.

---

## User Review Required

> [!IMPORTANT]
> - **Database Engine**: PostgreSQL is configured and running on `localhost:5432` with database `aria_db` and user `postgres`.
> - **Python Environment**: `backend/.venv` with Django 6.1, `psycopg`, `djangorestframework`, and `django-cors-headers`.
> - **Authentication**: Token/Session based auth supporting both HR Admin (`admin@aria.com`) and Employee Self-Service (`employee@aria.com` / custom created employees) with OTP verification and full profile management.

---

## Proposed Architecture & Models

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 Frontend (Vite)                    │
│   (AuthScreen, Command Centre, People, Attendance,          │
│    TimeOff, Payroll, Roster, ProfilePanel, Notifications)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON / CORS)
┌──────────────────────────────▼──────────────────────────────┐
│                    Django REST Backend                      │
│                                                             │
│  ├── accounts (User, Profile, Documents, OTP)              │
│  ├── attendance (AttendanceRecord, CheckIn/Out, Exceptions) │
│  ├── leaves (LeaveRequest, TeamAwayCalendar)                │
│  ├── payroll (SalaryStructure, PayrollRun, Payslips)        │
│  ├── roster (ShiftAssignment, TeamCoverage)                 │
│  └── core (Notifications, NotificationPreferences, Activity)│
└──────────────────────────────┬──────────────────────────────┘
                               │ psycopg
┌──────────────────────────────▼──────────────────────────────┐
│                PostgreSQL Database (aria_db)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Proposed Changes

### Backend Component (`backend/`)

#### 1. Configuration & App Setup
- **[MODIFY] [settings.py](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/backend/config/settings.py)**:
  - Configure PostgreSQL database (`ENGINE: 'django.db.backends.postgresql'`, `NAME: 'aria_db'`, `USER: 'postgres'`, `HOST: '127.0.0.1'`, `PORT: '5432'`).
  - Add `rest_framework`, `corsheaders`, `apps.accounts`, `apps.attendance`, `apps.leaves`, `apps.payroll`, `apps.roster`, `apps.core` to `INSTALLED_APPS`.
  - Add `corsheaders.middleware.CorsMiddleware` and configure `CORS_ALLOW_ALL_ORIGINS = True` (or `http://localhost:5173`).
  - Configure media upload paths for employee photos and documents.
- **[MODIFY] [urls.py](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/backend/config/urls.py)**:
  - Wire up API router prefixes: `/api/auth/`, `/api/employees/`, `/api/attendance/`, `/api/leaves/`, `/api/payroll/`, `/api/roster/`, `/api/notifications/`, `/api/dashboard/`.

#### 2. Django Apps & Models
- **[NEW] `apps/accounts/`**:
  - `User` model inheriting `AbstractUser` with fields: `employee_id`, `role` (`admin`/`employee`), `phone`, `birth_date`, `address`, `emergency_contact`, `emergency_phone`, `department`, `job_title`, `manager`, `employment_type`, `joining_date`, `location`, `shift`, `avatar_color`, `photo`.
  - `Document` model: `user`, `name`, `file`, `category`, `uploaded_at`.
  - `OTPVerification` model: `email`, `otp_code`, `created_at`, `is_verified`.
  - Serializers & Viewsets for Auth (Signin, Signup, Verify OTP, Me, Logout) and Employee Directory (list, retrieve, update, upload document/photo).
- **[NEW] `apps/attendance/`**:
  - `AttendanceRecord` model: `employee`, `date`, `status`, `check_in`, `check_out`, `work_hours`, `location`, `issue_note`, `is_exception`.
  - Views for live today attendance, weekly attendance pulse chart, exception resolution, check-in toggle, CSV export.
- **[NEW] `apps/leaves/`**:
  - `LeaveRequest` model: `employee`, `leave_type`, `start_date`, `end_date`, `reason`, `status` (`pending`/`approved`/`rejected`), `admin_comment`, `applied_at`.
  - Views for leave request list/filter, create leave request, resolve request (approve/reject), team away calendar.
- **[NEW] `apps/payroll/`**:
  - `SalaryStructure` model: `employee`, `basic`, `hra`, `special`, `other`, `deductions`.
  - `PayrollRun` model: `month`, `year`, `status`, `readiness_percentage`, `gross_amount`.
  - Views for payroll dashboard metrics, checklist validation, salary structure update, payslip download, report export.
- **[NEW] `apps/roster/`**:
  - `ShiftAssignment` model: `employee`, `date`, `shift_code` (`M`/`E`/`N`/`L`/`W`), `shift_name`.
  - Views for weekly roster schedule matrix, shift cycle update, roster publish action, team coverage metrics.
- **[NEW] `apps/core/`**:
  - `Notification` & `NotificationPreference` models.
  - `ActivityEvent` model.
  - Command Centre summary endpoint aggregating decision queue, live alignment metrics, 7-day signals, and live feed.
- **[NEW] `apps/core/management/commands/seed_data.py`**:
  - Comprehensive seed management command to populate the database with all initial employees (Arjun Mehta, Neha Sharma, Aisha Khan, Rohit Sharma, Priya Desai, Vikram Singh, Meera Iyer), attendance records, leave requests, payroll data, weekly roster, notifications, and activity logs.

---

### Frontend Component (`frontend/`)

#### 1. API Client & Service Layer
- **[NEW] [api.js](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/api.js)**:
  - Centralized API service with unified request handling, base URL (`http://127.0.0.1:8000/api`), token/session headers, error interceptors, and typed API endpoints.

#### 2. Component Integration (Remove Mock Data)
- **[MODIFY] [App.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/App.vue)**:
  - Load Command Centre data, pending requests, alignment stats, attendance pulse, and live feed dynamically from backend API.
  - Real-time resolution of leave decisions calling backend API.
- **[MODIFY] [AuthScreen.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/AuthScreen.vue)**:
  - Connect sign in, sign up, OTP verification, and password reset to backend auth endpoints.
- **[MODIFY] [EmployeeHome.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/EmployeeHome.vue)**:
  - Connect live check-in/check-out toggle, weekly attendance hours, and user leave/expense requests to backend.
- **[MODIFY] [PeoplePage.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/PeoplePage.vue)**:
  - Load active employees, department counts, filter/search, and employee detail drawer from backend.
- **[MODIFY] [AttendancePage.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/AttendancePage.vue)**:
  - Fetch live summary metrics, weekly chart bars, exceptions queue, and team attendance table from backend.
- **[MODIFY] [TimeOffPage.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/TimeOffPage.vue)**:
  - Fetch pending leave queue, summary capacity stats, and team away calendar from backend.
- **[MODIFY] [PayrollPage.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/PayrollPage.vue)**:
  - Fetch payroll pre-flight checks, employee salary structures, monthly trend chart; persist salary edits and run payroll validation through backend.
- **[MODIFY] [RosterPage.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/RosterPage.vue)**:
  - Fetch weekly schedule matrix; cycle shifts and publish roster updates to backend.
- **[MODIFY] [ProfilePanel.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/ProfilePanel.vue)**:
  - Fetch and save personal/job/salary details, upload documents, and download payslips via backend.
- **[MODIFY] [NotificationPanel.vue](file:///c:/Users/Atharva/Downloads/ODOO_Hackathon/frontend/src/components/NotificationPanel.vue)**:
  - Fetch live notifications, mark all as read, and update notification channel preferences via backend.

---

## Verification Plan

### Automated Verification
1. **Database Migrations & Seeding**:
   ```powershell
   .\.venv\Scripts\python.exe manage.py makemigrations
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py seed_data
   ```
2. **Django Unit / Endpoint Tests**:
   - Verify auth flow (signin, signup, otp verification).
   - Verify employee directory, attendance, leaves, payroll, and roster endpoints return 200 OK with valid PostgreSQL data.
3. **Frontend Build & Dev Validation**:
   - `pnpm run build` in `frontend/` to confirm zero build/lint errors.

### Manual Verification
1. Log in as HR Admin (`admin@aria.com` / `Aria@2026`) -> verify Command Centre, People, Attendance, Time Off, Payroll, Roster, Notifications.
2. Approve/reject a leave request -> verify state updates in PostgreSQL database and reflects across Command Centre & Time Off page.
3. Toggle check-in/out as Employee (`employee@aria.com`) -> verify live attendance record logged in PostgreSQL.
4. Update salary structure in Payroll and verify persistence in DB.
5. Create new account, complete OTP verification, and verify user profile created in PostgreSQL.
