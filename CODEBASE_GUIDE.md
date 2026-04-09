# HaminG — Codebase Developer Guide

> **Last updated:** 2026-04-07  
> **Purpose:** Help new developers quickly understand the project structure, components, and functions so they can fix bugs and implement features faster.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [File Structure (Tree)](#3-file-structure-tree)
4. [Backend — Deep Dive](#4-backend--deep-dive)
   - [Entry Point & App Setup](#41-entry-point--app-setup-mainpy)
   - [Database Layer](#42-database-layer)
   - [Models (ORM)](#43-models-orm-modelspy)
   - [Enums](#44-enums-enumspy)
   - [Schemas (Pydantic)](#45-schemas-pydantic-schemas)
   - [Authentication & Security](#46-authentication--security)
   - [Dependencies (Middleware-style)](#47-dependencies-dependenciespy)
   - [Routers (API Endpoints)](#48-routers-api-endpoints)
   - [Exercise Logic (CV/Pose)](#49-exercise-logic-cvpose)
   - [Middleware](#410-middleware)
   - [Auto Mail (Email Reports)](#411-auto-mail-auto_mailpy)
   - [Utility Scripts](#412-utility-scripts-scripts)
   - [Database Migrations](#413-database-migrations)
5. [Frontend — Deep Dive](#5-frontend--deep-dive)
   - [Entry Point & Configuration](#51-entry-point--configuration)
   - [Router](#52-router-routerjs)
   - [Vue Components](#53-vue-components)
   - [Brain Exercise Games](#54-brain-exercise-games-games)
6. [Deployment (Vercel)](#6-deployment-vercel)
7. [Environment Variables](#7-environment-variables)
8. [Common Tasks for Developers](#8-common-tasks-for-developers)

---

## 1. Project Overview

**HaminG** (also known as "Medic1") is a **rehabilitation management platform** for elderly patients in Vietnam. It connects **doctors** and **patients** and provides:

- AI-powered exercise tracking via camera (MediaPipe pose estimation)
- Weekly exercise plan management
- Brain training mini-games
- Doctor–patient messaging and scheduling
- AI-assisted health chatbot (Google Gemini)
- Wearable health data import (XML/JSON)
- Automated email health reports

The app uses **Vietnamese** for all user-facing text.

---

## 2. Tech Stack

| Layer       | Technology                                                    |
|-------------|---------------------------------------------------------------|
| Frontend    | **Vue 3** (Composition API) + **Vite** + **TailwindCSS**     |
| Backend     | **FastAPI** (Python) + **SQLAlchemy** ORM                     |
| Database    | **PostgreSQL** (hosted on Neon)                               |
| Auth        | **JWT** (python-jose) + **bcrypt** hashing + Google OAuth     |
| AI Chat     | **Google Gemini** (gemini-3-flash-preview) — streaming SSE    |
| Pose Est.   | **MediaPipe Tasks Vision** (client-side in browser)           |
| Charts      | **D3.js** for data visualization                              |
| Email       | **smtplib** (Gmail SMTP SSL)                                  |
| Deployment  | **Vercel** (static frontend + serverless Python backend)      |
| State Mgmt  | **Pinia**                                                     |

---

## 3. File Structure (Tree)

```
COS40005ComputingTechnologyProjectA/
│
├── api/                          # Vercel serverless entry point
│   └── index.py                  # Re-exports FastAPI app from backend/main.py
│
├── backend/                      # ⭐ Python FastAPI backend
│   ├── main.py                   # App initialization, CORS, exception handlers, router registration
│   ├── database.py               # SQLAlchemy engine, SessionLocal, get_db()
│   ├── models.py                 # All SQLAlchemy ORM models (15 tables)
│   ├── enums.py                  # Typed enums (UserRole, ExerciseType, statuses, etc.)
│   ├── auth.py                   # JWT creation/verification, bcrypt password utils
│   ├── dependencies.py           # FastAPI Depends() for auth, role checks, access control
│   ├── exceptions.py             # Custom exception classes
│   ├── utils.py                  # Pagination helper (Page model + paginate())
│   ├── auto_mail.py              # Email report generation & SMTP sending
│   ├── exercise_logic.py         # Backward-compat facade for pose exercise logic
│   ├── .env / .env.example       # Environment variables (DB, secrets, SMTP, Gemini)
│   │
│   ├── routers/                  # ⭐ API endpoint modules (one per domain)
│   │   ├── auth.py               # Login, signup (OTP), Google OAuth, forgot password
│   │   ├── patients.py           # Patient CRUD, search, create-by-doctor
│   │   ├── doctors.py            # Doctor listing
│   │   ├── medical_records.py    # Medical record CRUD
│   │   ├── assignments.py        # Exercise assignment CRUD
│   │   ├── exercises.py          # Workout sessions, exercise logs, pose processing
│   │   ├── plans.py              # Weekly plan CRUD
│   │   ├── schedules.py          # Appointment scheduling
│   │   ├── messages.py           # Doctor–patient messaging
│   │   ├── notifications.py      # In-app notification management
│   │   ├── dashboard.py          # Analytics: stats, charts, patient overview, trends
│   │   ├── ai_chat.py            # Gemini AI chatbot (streaming SSE)
│   │   ├── wearable.py           # Wearable device data upload & retrieval
│   │   └── websockets.py         # Live coaching WebSocket (session broadcast)
│   │
│   ├── schemas/                  # Pydantic request/response validation
│   │   ├── __init__.py           # Central re-export of all schemas
│   │   ├── user.py               # UserCreate, UserLogin, UserResponse, password validation...
│   │   ├── exercise.py           # Assignment, Combo, Session, WeekPlan, landmark schemas
│   │   ├── communication.py      # Schedule, Message, Notification, AI Chat schemas
│   │   └── medical.py            # MedicalRecord, PatientNote schemas
│   │
│   ├── logic/                    # Modular exercise counting logic
│   │   ├── common.py             # State classes (SquatState, etc.), Landmark, FeedbackPriority
│   │   ├── utils.py              # AngleCalculator (joint angles from landmarks)
│   │   ├── counter.py            # ExerciseCounter (state machine for rep counting)
│   │   └── strategies/           # Per-exercise strategy implementations
│   │       ├── base.py           # Base strategy interface
│   │       ├── squat.py          # Squat detection logic
│   │       ├── bicep_curl.py     # Bicep curl detection logic
│   │       ├── shoulder_flexion.py # Shoulder flexion detection logic
│   │       └── knee_raise.py     # Knee raise detection logic
│   │
│   ├── middleware/
│   │   └── ownership.py          # ResourceAccess class for resource-level auth guards
│   │
│   ├── scripts/                  # One-off utility scripts
│   │   ├── seed_data.py          # Seed database with demo data
│   │   ├── check_users.py        # List users in DB
│   │   ├── script_auth.py        # Auth testing utility
│   │   └── migrate_exercise_logs.py # Data migration script
│   │
│   ├── migrations/               # Raw SQL migration files
│   │   ├── 001_week_plans.sql
│   │   └── 002_unique_full_name.sql
│   │
│   ├── alembic/                  # Alembic migration framework
│   ├── alembic.ini
│   │
│   └── tests/                    # Backend test files
│
├── frontend/                     # ⭐ Vue 3 + Vite frontend
│   ├── index.html                # SPA entry point
│   ├── package.json              # Dependencies and scripts
│   ├── vite.config.js            # Vite build config (proxy /api → backend)
│   ├── tailwind.config.js        # Tailwind theme config
│   │
│   └── src/
│       ├── main.js               # Vue app creation, Pinia, router, global error handler
│       ├── App.vue               # Root component (<router-view>)
│       ├── config.js             # API_BASE_URL, APP_CONFIG constants
│       ├── router.js             # Vue Router — route definitions & auth guards
│       ├── style.css             # Global styles + Tailwind directives
│       │
│       ├── components/           # ⭐ Page-level Vue components (19 files)
│       │   ├── AuthLogin.vue           # Login/Signup/Forgot-password page
│       │   ├── MainLayout.vue          # Doctor's main layout (sidebar + content area)
│       │   ├── DoctorDashboard.vue     # Doctor analytics dashboard
│       │   ├── DoctorPatientDetail.vue # Doctor views a patient's detail & history
│       │   ├── DoctorMessaging.vue     # Doctor messaging interface
│       │   ├── DoctorScheduling.vue    # Doctor appointment scheduling
│       │   ├── PatientTabs.vue         # Patient's tab navigation wrapper
│       │   ├── PatientDashboard.vue    # Patient main dashboard (stats + health)
│       │   ├── PatientAssignment.vue   # Patient views/executes assigned exercises
│       │   ├── PatientWorkout.vue      # Camera-based workout with pose detection
│       │   ├── PatientScheduling.vue   # Patient views their appointments
│       │   ├── PatientMessaging.vue    # Patient messaging interface
│       │   ├── PatientContact.vue      # Patient's doctor contact info
│       │   ├── PatientManagement.vue   # Doctor's patient list management
│       │   ├── ExerciseLibrary.vue     # Browse exercises & combos
│       │   ├── BrainExercise.vue       # Brain training hub (game selection + stats)
│       │   ├── SportsTraining.vue      # Sports training tab
│       │   ├── AIChatbox.vue           # AI medical assistant chatbot (Gemini streaming)
│       │   └── FeedbackOverlay.vue     # Reusable feedback notification overlay
│       │
│       └── games/                # ⭐ Brain exercise mini-games (12 files)
│           ├── CardGame.vue            # Memory card matching
│           ├── CategoryGame.vue        # Category classification
│           ├── ColorGame.vue           # Color recognition
│           ├── ComparisonGame.vue      # Size/number comparison
│           ├── MathGame.vue            # Arithmetic exercises
│           ├── MemoryGame.vue          # Sequence memory
│           ├── OddOneOutGame.vue       # Find the odd item
│           ├── PatternGame.vue         # Pattern recognition
│           ├── ReflexGame.vue          # Reaction time
│           ├── ShadowMatchGame.vue     # Shape matching
│           ├── TrueFalseGame.vue       # True/false quizzes
│           └── WordGame.vue            # Word puzzles
│
├── tests/                        # Project-level documentation & test reports
│   ├── DEMO_WORKFLOW.md
│   ├── WEBSITE_FUNCTIONS_FULL_INVENTORY_2026-04-04.md
│   └── ... (various reports)
│
├── vercel.json                   # Vercel deployment config (builds, routes, env)
├── requirements.txt              # Python dependencies
├── DOCUMENTATION.md              # Existing project documentation
└── README.md                     # Project README
```

---

## 4. Backend — Deep Dive

### 4.1. Entry Point & App Setup (`main.py`)

| What it does | Details |
|---|---|
| Creates the FastAPI app | `FastAPI(title="HaminG Rehabilitation API", version="2.1")` |
| CORS | Allows `localhost:3000/5173/4173` and `haming.vercel.app` |
| Exception handlers | Custom handlers for validation, SQLAlchemy, HTTP, and unhandled errors |
| Router registration | Includes **13 routers** (auth, patients, exercises, dashboard, ai_chat, etc.) |
| Legacy endpoints | `/api/doctor-id` — smart doctor lookup for patients; `/api/send-report-email` — trigger email report |
| Database init | `Base.metadata.create_all()` runs at module load (for Vercel cold starts) |
| Startup validation | `validate_environment()` checks required env vars |

**To run locally:**
```bash
cd backend
uvicorn main:app --reload --port 8001
```

---

### 4.2. Database Layer

**`database.py`** sets up:
- `engine` — SQLAlchemy engine connected to PostgreSQL (Neon) via `DATABASE_URL`
- `SessionLocal` — Session factory with connection pooling (`pool_size=5`, `max_overflow=10`)
- `get_db()` — FastAPI dependency that yields a DB session per request

> ⚠️ The fallback `DATABASE_URL` is hardcoded for development. **Never commit production credentials.**

---

### 4.3. Models (ORM) — `models.py`

There are **15 SQLAlchemy models** (database tables):

| Model | Table | Purpose |
|-------|-------|---------|
| `User` | `users` | All users (doctors & patients). Has `role`, `status`, `last_active_at`. Central entity with many relationships. |
| `ExerciseLogSimple` | `exercise_logs_simple` | Legacy exercise log (date, exercise_type, rep_count, feedback) |
| `Schedule` | `schedules` | Doctor–patient appointments (start/end time, status, session_type) |
| `Assignment` | `assignments` | Exercise assignments from doctor to patient (exercise_type, target_reps, frequency, day_of_week, sets) |
| `Message` | `messages` | Direct messages between users (content, is_read) |
| `Combo` | `combos` | Exercise combo templates created by doctors |
| `ComboItem` | `combo_items` | Individual exercises within a combo (sequence_order, target_reps) |
| `WorkoutSession` | `workout_sessions` | A workout session (start/end time, status: in_progress/completed/abandoned) |
| `SessionDetail` | `session_details` | Per-exercise results within a session (reps, duration, mistakes, accuracy_score, feedback) |
| `BrainExerciseLog` | `brain_exercise_logs` | Individual brain exercise answers (exercise_type, is_correct, question_number) |
| `BrainExerciseSession` | `brain_exercise_sessions` | Summary of a brain exercise session (score, total_questions, percentage) |
| `MedicalRecord` | `medical_records` | Patient's medical info (diagnosis, symptoms, treatment_plan, height, weight, blood_type). One-per-patient. |
| `PatientNote` | `patient_notes` | Doctor's notes about a patient (title, content) |
| `WeekPlan` | `week_plans` | Weekly rehabilitation plans (plan_name, start/end dates, status). Has child `assignments`. |
| `Notification` | `notifications` | In-app notifications (title, message, type, is_read) |
| `OTPVerification` | `otp_verifications` | Temporary OTP storage for signup/password reset (email, otp_code, expires_at, user_data as JSON) |
| `WearableHealthData` | `wearable_health_data` | Uploaded smartwatch data (heart rate, calories, SpO2, sleep quality, per week) |

**Key Relationships:**
```
User ──┬── schedules_as_patient / schedules_as_doctor
       ├── assignments_as_patient / assignments_as_doctor
       ├── sent_messages / received_messages
       ├── combos (doctor only)
       ├── workout_sessions → session_details
       ├── exercise_logs
       ├── medical_record (one-to-one)
       ├── patient_notes / doctor_notes
       ├── week_plans_as_patient / week_plans_as_doctor → assignments
       ├── notifications
       └── wearable_data
```

---

### 4.4. Enums (`enums.py`)

| Enum | Values | Used for |
|------|--------|----------|
| `UserRole` | `doctor`, `patient` | `User.role` |
| `ExerciseType` | `bicep-curl`, `shoulder-flexion`, `squat`, `knee-raise` | Exercise identification |
| `ScheduleStatus` | `scheduled`, `completed`, `cancelled`, `rescheduled` | `Schedule.status` |
| `AssignmentStatus` | `active`, `completed`, `cancelled`, `expired` | `Assignment.status` |
| `SessionStatus` | `in_progress`, `completed`, `abandoned` | `WorkoutSession.status` |
| `WeekPlanStatus` | `active`, `completed`, `cancelled`, `draft` | `WeekPlan.status` |
| `NotificationType` | `info`, `warning`, `success`, `error`, `reminder` | `Notification.type` |
| `PatientStatus` | `active`, `inactive`, `needs_attention` | Activity-based patient status |
| `SessionType` | `consultation`, `checkup`, `therapy`, `followup` | `Schedule.session_type` |
| `AppointmentRequestStatus` | `pending`, `resolved`, `rejected` | Appointment request flow |

Also exports `DAILY_TARGETS` dict (default 10 reps for each exercise type).

---

### 4.5. Schemas (Pydantic) — `schemas/`

Schemas are organized by domain and exported from `schemas/__init__.py`:

| File | Schemas | Purpose |
|------|---------|---------|
| `user.py` | `UserCreate`, `UserLogin`, `UserUpdate`, `UserResponse`, `UserWithToken`, `UserListItem`, `PatientCreate`, `PatientResponse`, `DoctorResponse`, `GoogleLogin`, `ForgotPasswordRequest`, `VerifyForgotPasswordOTP`, `ResetPassword` | User auth & profile validation. Includes **password strength validation** (8+ chars, uppercase, lowercase, digit, special char). |
| `exercise.py` | `AssignmentCreate/Update/Response`, `ComboItemCreate/Response`, `ComboCreate/Update/Response`, `SessionDetailCreate/Response`, `WorkoutSessionCreate/End/Response`, `ExerciseLogCreate/Response`, `WeekPlanCreate/Update/Response`, `OverallStatsResponse`, `WeeklyProgressResponse`, `LandmarkData`, `ProcessRequest`, `ProcessResponse` | Exercise assignments, combos, workout sessions, week plans, and camera landmark processing. |
| `communication.py` | `ScheduleCreate/Update/Response`, `MessageCreate/Update/Response`, `NotificationCreate/Update/Response`, `AIChatRequest`, `AIChatResponse` | Scheduling, messaging, notifications, and AI chat. |
| `medical.py` | `MedicalRecordCreate/Update/Response`, `PatientNoteCreate/Update/Response` | Medical records and doctor notes. |

---

### 4.6. Authentication & Security (`auth.py`)

| Function | Purpose |
|----------|---------|
| `verify_password(plain, hashed)` | Checks password using `bcrypt.checkpw()`. Falls back to plain text comparison (legacy). |
| `get_password_hash(password)` | Hashes password using `bcrypt.hashpw()` with auto-generated salt. |
| `create_access_token(data, expires_delta)` | Creates a JWT token with `sub` (user_id) and `role`. Default expiry: 30 min. |
| `verify_token(token)` | Decodes and validates JWT token. Returns payload or `None`. |

**Key configs:**
- `SECRET_KEY` — loaded from env, **must** be set (runtime error if missing/default)
- `ALGORITHM` — defaults to `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES` — defaults to `30`

---

### 4.7. Dependencies (`dependencies.py`)

These are FastAPI `Depends()` functions used to protect endpoints:

| Dependency | What it does |
|------------|--------------|
| `get_current_user` | Extracts JWT → fetches `User` from DB. Returns `User` or raises `401`. |
| `get_current_doctor` | Wraps `get_current_user` + role check (`doctor` only). Raises `403`. |
| `get_current_patient` | Wraps `get_current_user` + role check (`patient` only). Raises `403`. |
| `verify_patient_access(patient_id)` | Doctors can access any patient; patients can only access their own data. |
| `verify_doctor_patient_relationship(patient_id)` | Checks patient exists. Currently **relaxed** — any doctor can access any patient. |
| `verify_assignment_access(assignment_id)` | Doctors access their assignments; patients access assignments assigned to them. |
| `verify_medical_record_access(patient_id)` | Delegates to `verify_patient_access`. |
| `optional_auth` | Returns `User` if valid token, `None` otherwise. For optional auth endpoints. |
| `validate_environment()` | Checks `SECRET_KEY` and `DATABASE_URL` are set. Called at startup. |

---

### 4.8. Routers (API Endpoints)

All routers are prefixed with `/api` (or `/api/ai`, `/api/wearable`).

#### `routers/auth.py` — Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login` | POST | Email + password login → returns JWT token |
| `/api/signup/request-otp` | POST | Send OTP email for new user registration |
| `/api/signup/verify-otp` | POST | Verify OTP → create user → return JWT |
| `/api/forgot-password/request-otp` | POST | Send OTP for password reset |
| `/api/forgot-password/verify-otp` | POST | Verify forgot-password OTP |
| `/api/forgot-password/reset` | POST | Reset password with valid OTP |
| `/api/google` | POST | Google OAuth login (auto-creates patient if new) |
| `/api/me` | GET | Get current authenticated user info |

#### `routers/patients.py` — Patient Management
Handles patient listing, search, CRUD, and doctor-created patient accounts.

#### `routers/doctors.py` — Doctor Management
Doctor listing and lookup.

#### `routers/medical_records.py` — Medical Records
CRUD for patient medical records (diagnosis, symptoms, treatment plan, vitals).

#### `routers/assignments.py` — Exercise Assignments
CRUD for exercise assignments from doctors to patients.

#### `routers/exercises.py` — Workouts & Pose Processing
- Workout session start/end
- Exercise log recording
- **Landmark processing** — receives MediaPipe pose landmarks, runs through exercise counter, returns rep counts + feedback
- Brain exercise logging and stats

#### `routers/plans.py` — Weekly Plans
CRUD for `WeekPlan` (doctor creates a weekly rehab plan with multiple daily exercises).

#### `routers/schedules.py` — Appointment Scheduling
CRUD for doctor–patient appointments. Supports status updates (scheduled → completed/cancelled).

#### `routers/messages.py` — Messaging
Send/receive messages between doctors and patients. Mark messages as read.

#### `routers/notifications.py` — Notifications
Create, list, and mark-as-read in-app notifications.

#### `routers/dashboard.py` — Analytics & Dashboard
| Endpoint | Description |
|----------|-------------|
| `/api/overall-stats` | Total sessions, reps, duration, active days for a patient |
| `/api/weekly-progress` | Last 10 exercise session details |
| `/api/patient/charts/{id}` | Weekly activity, accuracy trend, muscle focus charts |
| `/api/patient/overview/{id}` | **Aggregated** endpoint: sessions + logs + notes + charts + stats in one call |
| `/api/today-progress` | Today's activity across all patients (for doctor dashboard) |
| `/api/dashboard/summary` | Dashboard KPIs: total patients, active/inactive counts, trends |
| `/api/patients-with-status` | All patients with activity status (active/needs_attention/inactive) |
| `/api/patient/health-metrics/{id}` | Derived health metrics (heart rate, calories, SpO2, sleep) |
| `/api/patient/health-charts/{id}` | 7-day heart rate and rep charts |

#### `routers/ai_chat.py` — AI Medical Assistant
| Endpoint | Description |
|----------|-------------|
| `/api/ai/chat` | POST — Takes a message + patient_id, builds rich patient context (medical records, workout history, notes), sends to **Gemini**, returns **streaming SSE response**. |

The system prompt instructs Gemini to act as a Vietnamese-speaking medical AI assistant with access to the patient's exercise data, medical records, and doctor notes.

#### `routers/wearable.py` — Wearable Data
| Endpoint | Description |
|----------|-------------|
| `/api/wearable/upload` | POST — Upload smartwatch weekly summary (heart rate, calories, SpO2, sleep) |
| `/api/wearable/latest/me` | GET — Get authenticated user's latest wearable data |
| `/api/wearable/latest/{user_id}` | GET — Get a specific user's latest wearable data |

#### `routers/websockets.py` — Live Coaching
| Endpoint | Description |
|----------|-------------|
| `/ws/session/{session_id}` | WebSocket — Live workout session broadcast. JWT-authenticated via query param. Uses `ConnectionManager` to broadcast rep updates to all connected observers (doctors). |

---

### 4.9. Exercise Logic (CV/Pose)

Located in `logic/` directory with a backward-compat facade in `exercise_logic.py`.

| File | Purpose |
|------|---------|
| `logic/common.py` | State machine constants (`SquatState`, `BicepCurlState`, `ShoulderFlexionState`, `KneeRaiseState`), `FeedbackPriority`, and `Landmark` data class |
| `logic/utils.py` | `AngleCalculator` — static methods to calculate joint angles (knee, bicep, shoulder flexion, elbow-torso, vertical angle, etc.) from 3D landmarks |
| `logic/counter.py` | `ExerciseCounter` — main state machine that processes landmarks and counts reps for each exercise type using strategy pattern |
| `logic/strategies/base.py` | Base strategy interface |
| `logic/strategies/squat.py` | Squat detection: tracks knee angle through IDLE → START → DOWN → HOLD → UP cycle |
| `logic/strategies/bicep_curl.py` | Bicep curl detection: tracks elbow angle |
| `logic/strategies/shoulder_flexion.py` | Shoulder flexion detection: tracks shoulder-hip-wrist angle |
| `logic/strategies/knee_raise.py` | Knee raise detection: tracks hip-knee angle |
| `exercise_logic.py` | Backward-compat wrapper — exposes `calculate_all_angles()` and global `EXERCISE_COUNTER` |

**Flow:**
1. Frontend captures webcam → runs MediaPipe → sends 33 landmarks to backend
2. `exercises.py` router receives landmarks
3. `ExerciseCounter` processes through strategy pattern
4. Returns: rep counts per exercise, state names, and form feedback

---

### 4.10. Middleware

**`middleware/ownership.py`** — `ResourceAccess` class:

| Method | Guards access to |
|--------|------------------|
| `ResourceAccess.patient(patient_id)` | Patient data (self-only for patients, any for doctors) |
| `ResourceAccess.session(session_id)` | Workout sessions |
| `ResourceAccess.brain_session(session_id)` | Brain exercise sessions |
| `ResourceAccess.brain_log(log_id)` | Brain exercise logs |
| `ResourceAccess.assignment(assignment_id)` | Exercise assignments |
| `ResourceAccess.schedule(schedule_id)` | Scheduled appointments |

Used as FastAPI `Depends()` in routers and WebSocket handlers.

---

### 4.11. Auto Mail (`auto_mail.py`)

Generates and sends **HTML rehabilitation progress reports** via Gmail SMTP SSL.

| Function | Purpose |
|----------|---------|
| `gen_health_data(name)` | Generates random patient health data (weight, height, heart rate, blood pressure, etc.) |
| `calc_bmi(data)` | Calculates BMI and adds status label (underweight/normal/overweight/obese) |
| `gen_workout_data()` | Generates a random rehab workout session (exercise, duration, recovery score, pain level) |
| `gen_weekly_sessions(n)` | Generates `n` random workout sessions for the week |
| `build_email_html(health, sessions)` | Builds a rich HTML email with health metrics table, weekly summary cards, and per-session detail table |
| `send_health_email(receiver, name)` | Orchestrates data generation + email sending. Supports comma-separated multiple recipients. |

> 📧 Requires `SENDER_EMAIL` and `SENDER_PASSWORD` env vars (Gmail App Password).

---

### 4.12. Utility Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `seed_data.py` | Seeds the database with demo doctors, patients, assignments, sessions, and medical records |
| `check_users.py` | Quick script to list all users in the DB |
| `script_auth.py` | Test authentication flow |
| `migrate_exercise_logs.py` | Migrate data from legacy exercise_logs table format |

---

### 4.13. Database Migrations

- **`migrations/`** — Raw SQL migration files (manual)
  - `001_week_plans.sql` — Creates week_plans table
  - `002_unique_full_name.sql` — Adds unique constraint
- **`alembic/`** — Alembic migration framework (auto-generated from model changes)

---

## 5. Frontend — Deep Dive

### 5.1. Entry Point & Configuration

| File | Purpose |
|------|---------|
| `index.html` | SPA mount point (`<div id="app">`) |
| `main.js` | Creates Vue app, registers Pinia + Router, sets up global error handler |
| `config.js` | Exports `API_BASE_URL` (from env `VITE_API_BASE_URL` or `/api`), `CAMERA_API_URL`, and `APP_CONFIG` (name, tagline, version) |
| `style.css` | Global CSS with Tailwind directives + custom styles |
| `App.vue` | Root component — just renders `<router-view>` |

### 5.2. Router (`router.js`)

| Route | Component | Access |
|-------|-----------|--------|
| `/` | Redirect → `/login` | Public |
| `/login` | `AuthLogin.vue` | Public (redirects to dashboard if already logged in) |
| `/patient` | `PatientTabs.vue` | Auth required, `patient` role only |
| `/doctor` | `MainLayout.vue` | Auth required, `doctor` role only |
| `/dashboard` | `DoctorDashboard.vue` | Auth required |
| `/*` (catch-all) | Redirect → `/login` | — |

**Navigation guards:**
1. Unauthenticated users trying to access protected routes → redirected to `/login`
2. Authenticated users trying to access `/login` → redirected to their role-specific dashboard
3. Role mismatch (e.g., patient trying to access `/doctor`) → redirected to correct dashboard

**Auth state** is stored in `localStorage`:
- `token` — JWT string
- `user` — JSON-serialized user object (with `role`, `user_id`, etc.)

---

### 5.3. Vue Components

#### Auth & Layout

| Component | Description |
|-----------|-------------|
| **`AuthLogin.vue`** (36KB) | Full authentication page: login form, registration with OTP email verification, Google OAuth, forgot password flow. All UI text in Vietnamese. |
| **`MainLayout.vue`** (16KB) | Doctor's main layout shell with sidebar navigation (patients, schedules, messages, exercises, AI chat, brain exercises) and responsive design. |
| **`PatientTabs.vue`** (7KB) | Patient's tab-based navigation. Hosts patient sub-pages as tabs (Dashboard, Exercises, Schedule, Messages, Contact). |
| **`FeedbackOverlay.vue`** (5KB) | Reusable overlay for form-feedback during exercise sessions. |

#### Doctor Views

| Component | Description |
|-----------|-------------|
| **`DoctorDashboard.vue`** (37KB) | Main analytics dashboard for doctors. Shows: patient count KPIs with trends, active/inactive breakdown, today's activity feed, patient status cards (active/needs_attention/inactive). Uses D3.js for charts. |
| **`DoctorPatientDetail.vue`** (15KB) | Doctor drills into a specific patient. Shows: session history, exercise logs, patient notes (CRUD), medical records, performance charts, and AI chat trigger. |
| **`DoctorMessaging.vue`** (17KB) | Doctor's messaging interface. Contact list + conversation thread. Real-time polling for new messages. |
| **`DoctorScheduling.vue`** (36KB) | Appointment management for doctors. Calendar view, create/edit/cancel appointments, filter by status. |
| **`PatientManagement.vue`** (14KB) | Doctor's patient list. Search, filter by status, create new patients, navigate to patient detail. |
| **`ExerciseLibrary.vue`** (31KB) | Browse, create, edit exercise combos and individual assignments. Assign exercises to patients. |

#### Patient Views

| Component | Description |
|-----------|-------------|
| **`PatientDashboard.vue`** (30KB) | Patient's main dashboard. Shows: overall stats (total sessions, reps, duration), health metrics cards (heart rate, calories, SpO2, sleep), health trend charts (D3.js), and wearable data import (XML upload). |
| **`PatientAssignment.vue`** (46KB) | Patient views assigned exercises and weekly plans. Start a workout session, track progress per exercise, mark assignments complete. |
| **`PatientWorkout.vue`** (37KB) | **Camera-based exercise tracking.** Uses MediaPipe Tasks Vision for real-time pose detection, sends landmarks to backend for rep counting, displays live feedback and rep counter. |
| **`PatientScheduling.vue`** (16KB) | Patient views upcoming appointments, request appointment changes. |
| **`PatientMessaging.vue`** (14KB) | Patient messaging with their doctor(s). |
| **`PatientContact.vue`** (9KB) | Patient views their assigned doctor's contact information. |

#### AI & Brain Training

| Component | Description |
|-----------|-------------|
| **`AIChatbox.vue`** (27KB) | AI medical chatbot. Sends messages to `/api/ai/chat`, handles streaming SSE response from Gemini, renders markdown responses. Context-aware (works with specific patient data). |
| **`BrainExercise.vue`** (39KB) | Brain training hub. Game selection grid, difficulty settings, session history and score tracking, performance charts. Launches individual game components. |
| **`SportsTraining.vue`** (24KB) | Sports training tab for general fitness exercises. |

---

### 5.4. Brain Exercise Games (`games/`)

12 mini-games for cognitive rehabilitation:

| Game | File | Description |
|------|------|-------------|
| Card Match | `CardGame.vue` | Flip and match pairs of cards |
| Category Sort | `CategoryGame.vue` | Classify items into correct categories |
| Color Match | `ColorGame.vue` | Identify colors and color-word conflicts (Stroop-like) |
| Comparison | `ComparisonGame.vue` | Compare sizes or numbers |
| Math | `MathGame.vue` | Basic arithmetic exercises |
| Memory | `MemoryGame.vue` | Remember and recall sequences |
| Odd One Out | `OddOneOutGame.vue` | Find the item that doesn't belong |
| Pattern | `PatternGame.vue` | Identify and continue patterns |
| Reflex | `ReflexGame.vue` | Reaction time challenges |
| Shadow Match | `ShadowMatchGame.vue` | Match shapes to their silhouettes |
| True/False | `TrueFalseGame.vue` | Answer true/false quiz questions |
| Word Puzzle | `WordGame.vue` | Word completion and scramble exercises |

Each game records results to the backend (`brain_exercise_logs` and `brain_exercise_sessions` tables) for progress tracking.

---

## 6. Deployment (Vercel)

**`vercel.json`** configures:

| Build | Source | Builder |
|-------|--------|---------|
| Frontend | `frontend/package.json` | `@vercel/static-build` → outputs `dist/` |
| API | `api/index.py` | `@vercel/python` (serverless function) |

**Routes:**
- `/api/*` → `api/index.py` (FastAPI serverless)
- `/assets/*` → `frontend/assets/`
- `/*` (fallback) → `frontend/index.html` (SPA client-side routing)

**`api/index.py`** simply adds `backend/` to the Python path and re-exports `app` from `main.py`.

**Live URL:** `https://haming.vercel.app`

---

## 7. Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string (Neon) |
| `SECRET_KEY` | ✅ | JWT signing secret (must be strong, unique) |
| `ALGORITHM` | ❌ | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | Token expiry (default: `30`) |
| `GEMINI_API_KEY` | ❌ | Google Gemini API key (for AI chat) |
| `GOOGLE_CLIENT_ID` | ❌ | Google OAuth client ID |
| `SMTP_EMAIL` | ❌ | Gmail address for OTP emails |
| `SMTP_PASSWORD` | ❌ | Gmail App Password for OTP emails |
| `SENDER_EMAIL` | ❌ | Gmail address for health report emails |
| `SENDER_PASSWORD` | ❌ | Gmail App Password for health reports |
| `RECEIVER_EMAIL` | ❌ | Default recipient for health reports |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | ❌ | Backend API base URL (default: `/api`) |

---

## 8. Common Tasks for Developers

### Adding a New API Endpoint
1. Create or edit a router in `backend/routers/`
2. Define Pydantic schemas in `backend/schemas/` if needed
3. Register the router in `backend/main.py` (`app.include_router(...)`)
4. Add any new models to `backend/models.py`

### Adding a New Frontend Page
1. Create a `.vue` component in `frontend/src/components/`
2. Add a route in `frontend/src/router.js`
3. Add navigation link in `MainLayout.vue` (doctor) or `PatientTabs.vue` (patient)

### Adding a New Brain Game
1. Create a new `.vue` file in `frontend/src/games/`
2. Register it in `BrainExercise.vue` game list
3. Results auto-save via existing brain exercise log API

### Adding a New Exercise Type
1. Add to `ExerciseType` enum in `backend/enums.py`
2. Create a strategy in `backend/logic/strategies/`
3. Register in `ExerciseCounter` (`backend/logic/counter.py`)
4. Update frontend exercise selection UI

### Running the Project Locally
```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # configure your env vars
uvicorn main:app --reload --port 8001

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Seeding Demo Data
```bash
cd backend
python scripts/seed_data.py
```

---

> **Questions?** Check `DOCUMENTATION.md` for additional context, or `tests/DEMO_WORKFLOW.md` for a full walkthrough of the app features.
