# 🏥 HaminG — Elderly Rehabilitation Care Platform

> **Live Production:** [https://haming.vercel.app](https://haming.vercel.app)

A full-stack web application for managing elderly rehabilitation care. Doctors can monitor patient progress, assign exercise plans, track workout sessions, and communicate with patients — all in one place. Patients can view their schedules, perform guided AI-assisted exercises, and message their doctors.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Architecture Overview](#-architecture-overview)
- [Database Schema](#-database-schema)
- [Getting Started (Local Development)](#-getting-started-local-development)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Password Security Rules](#-password-security-rules)
- [Running Tests](#-running-tests)
- [Deployment to Vercel](#-deployment-to-vercel)
- [Key UI Pages](#-key-ui-pages)

---

## ✨ Features

### For Doctors

- **Dashboard** — Real-time overview of all patients with status indicators (Active / Needs Attention / Inactive), numbered patient list, progress bars, and a rich patient detail panel
- **AI Health Assistant** — Premium, context-aware AI chat for analyzing patient performance, medical history, and generating treatment insights
- **Patient Detail** — Click any patient to see:
  - Weekly activity bar chart (reps per day)
  - Accuracy trend line chart (last 10 sessions)
  - Exercise distribution breakdown
  - Key stats: total reps, sessions, active days, average accuracy
- **Exercise Assignment** — Assign exercise plans, create weekly schedules, and manage exercise combos
- **Messaging** — Real-time in-app messaging with patients
- **Medical Records** — Create/update patient diagnoses, symptoms, treatment plans, vitals
- **Doctor Notes** — Add private clinical notes per patient

### For Patients

- **Patient Dashboard** — Today's exercises, heart rate, calories, sleep quality, and weekly activity charts derived from real workout data
- **AI-Guided Exercises** — Camera-based pose detection for guided physiotherapy exercises
- **Brain Exercises** — Cognitive training games
- **Scheduling** — View upcoming appointments
- **Messaging** — Message your assigned doctor
- **AI Health Assistant** — Premium chat interface for personal health analysis, exercise feedback, and recovery tracking (powered by Gemini 3 Flash)

### Authentication

- Email-based signup with **OTP verification** sent to your email
- Secure **Forgot Password** flow (email → OTP → new password)
- **Google OAuth** login support
- **JWT tokens** for all protected routes

---

## 🛠 Tech Stack

| Layer          | Technology                                                          |
| -------------- | ------------------------------------------------------------------- |
| **Frontend**   | Vue 3 (Composition API), Vite, D3.js, Lucide Icons, TailwindCSS     |
| **Backend**    | Python 3.13, FastAPI, SQLAlchemy ORM, Alembic (migrations)          |
| **Database**   | PostgreSQL (production via Neon/Supabase), SQLite (local/test)      |
| **Auth**       | JWT (python-jose), bcrypt password hashing (passlib), Google OAuth2 |
| **Email**      | SMTP via Gmail (OTP verification)                                   |
| **Deployment** | Vercel (frontend + serverless backend via `/api/index.py`)          |
| **Testing**    | pytest, FastAPI TestClient, in-memory SQLite                        |

---

## 📁 Project Structure

```
HaminG_Le_Minh/
├── frontend/                    # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.vue            # Auth: login, signup (OTP), forgot password
│   │   │   ├── Dashboard.vue        # Doctor dashboard: patient list + charts
│   │   │   ├── DoctorPatientDetail.vue  # Patient detail view (tabs)
│   │   │   ├── PatientDashboard.vue # Patient's own health dashboard
│   │   │   ├── PatientWorkout.vue   # AI-guided exercise session
│   │   │   ├── BrainExercise.vue    # Cognitive training games
│   │   │   ├── Scheduling.vue       # Doctor scheduling
│   │   │   ├── Assignment.vue       # Exercise assignment manager
│   │   │   ├── DoctorMessaging.vue  # Doctor chat interface
│   │   │   ├── PatientMessaging.vue # Patient chat interface
│   │   │   ├── ExerciseLibrary.vue  # Exercise catalogue
│   │   │   ├── SportsTraining.vue   # Training management
│   │   │   ├── PatientTabs.vue      # Patient navigation tabs
│   │   │   ├── PatientManagement.vue
│   │   │   └── index.vue            # Main app shell / navigation
│   │   ├── router.js                # Vue Router routes
│   │   ├── config.js                # API_BASE_URL config
│   │   ├── style.css                # Global styles
│   │   └── main.js                  # App entry point
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # FastAPI backend
│   ├── routers/
│   │   ├── auth.py              # Login, Signup OTP, Forgot Password, Google OAuth
│   │   ├── dashboard.py         # Doctor dashboard stats, patient charts
│   │   ├── patients.py          # Patient CRUD, search
│   │   ├── medical_records.py   # Medical record read/write
│   │   ├── assignments.py       # Exercise assignment management
│   │   ├── schedules.py         # Appointment scheduling
│   │   ├── exercises.py         # Exercise sessions & logs
│   │   ├── messages.py          # In-app messaging
│   │   ├── plans.py             # Week exercise plans
│   │   ├── doctors.py           # Doctor-specific endpoints
│   │   └── notifications.py     # Notification system
│   ├── schemas/
│   │   ├── user.py              # User/Auth Pydantic schemas + password validation
│   │   ├── exercise.py          # Exercise schemas
│   │   ├── medical.py           # Medical record schemas
│   │   └── communication.py     # Message/notification schemas
│   ├── models.py                # SQLAlchemy database models
│   ├── database.py              # Database connection & session
│   ├── auth.py                  # JWT token creation & password hashing
│   ├── dependencies.py          # FastAPI dependency injection (get_current_user)
│   ├── enums.py                 # Shared enumerations
│   ├── main.py                  # FastAPI app entry point + middleware
│   ├── auto_mail.py             # Email report sender
│   ├── exercise_logic.py        # AI pose detection logic
│   ├── requirements.txt         # Python dependencies
│   ├── alembic.ini              # Alembic migrations config
│   └── tests/
│       └── test_auth_endpoints.py  # Pytest test suite (9 tests)
│
├── api/
│   └── index.py                 # Vercel serverless entry point
│
├── vercel.json                  # Vercel deployment config
└── README.md
```

---

## 🏛 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Vercel CDN                         │
│   ┌───────────────────┐   ┌───────────────────────────┐ │
│   │  Frontend (Vue3)  │   │  Backend (FastAPI)         │ │
│   │  /frontend/dist   │   │  /api/index.py (serverless)│ │
│   └─────────┬─────────┘   └──────────┬────────────────┘ │
└─────────────│────────────────────────│──────────────────┘
              │ HTTPS                  │ SQL
              ▼                        ▼
         Browser               PostgreSQL DB
                                (Neon / Supabase)
```

**Request Flow:**

1. Browser loads the Vue SPA from Vercel's CDN.
2. Vue Router handles client-side navigation.
3. API calls go to `/api/*`, routed to the Python serverless function.
4. FastAPI processes the request, queries PostgreSQL, and returns JSON.
5. JWT token in `Authorization: Bearer <token>` header authenticates all protected routes.

---

## 🗄 Database Schema

```
users               ← Core user table (doctors & patients)
  └─ medical_record
  └─ patient_notes
  └─ workout_sessions
       └─ session_details     ← Per-exercise accuracy scores & reps
  └─ exercise_logs_simple
  └─ assignments
  └─ schedules
  └─ messages (sent/received)
  └─ week_plans
  └─ notifications

brain_exercise_sessions      ← Cognitive game results
brain_exercise_logs          ← Per-question brain exercise logs
combos / combo_items         ← Doctor-defined exercise combos
otp_verifications            ← Temporary OTP records for signup/reset
```

**Patient Status** is calculated dynamically from `workout_sessions`:

- `active` — worked out in the last 3 days
- `needs_attention` — last workout was 3–7 days ago
- `inactive` — no workout in over 7 days

---

## 🚀 Getting Started (Local Development)

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.11
- **PostgreSQL** (or use the included SQLite for local testing)
- **Git**

### 1. Clone the repository

```bash
git clone git@github.com:HaMinhNX/COS40005ComputingTechnologyProjectA.git
cd COS40005ComputingTechnologyProjectA
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

#this is used in Tuan Dat Machine every time created
source /home/tuandat/ProjectB/backend/.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file (see Environment Variables section below)
cp .env.example .env   # or create manually

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --reload --port 8001
```

The API will be available at **http://localhost:8001**  
Interactive API docs: **http://localhost:8001/docs**

### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at **http://localhost:5173**

> **Note:** In development, the frontend proxies `/api` requests to `http://localhost:8001` via Vite's proxy config.

---

## 🔐 Environment Variables

Create a `backend/.env` file with these variables:

```env
# --- Database ---
DATABASE_URL=postgresql://user:password@host:5432/haming_db

# --- Security ---
SECRET_KEY=your-super-secret-jwt-key-at-least-32-characters-long
ALGORITHM=HS256

# --- Email (Gmail SMTP for OTP) ---
SMTP_EMAIL=your-gmail@gmail.com
SMTP_PASSWORD=your-gmail-app-password    # Use Gmail App Password, not main password

# --- Google OAuth (optional) ---
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

**How to get `SMTP_PASSWORD`:**

1. Enable 2FA on your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate an app password and paste it here

**For local testing with SQLite**, you can set:

```env
DATABASE_URL=sqlite:///./test.db
```

---

## 📡 API Reference

All endpoints are prefixed with `/api`.

### Authentication

| Method | Endpoint                           | Description                                     |
| ------ | ---------------------------------- | ----------------------------------------------- |
| `POST` | `/api/login`                       | Login with email + password                     |
| `POST` | `/api/signup/request-otp`          | Start signup — validates data & sends OTP email |
| `POST` | `/api/signup/verify-otp`           | Verify OTP → creates account & returns JWT      |
| `POST` | `/api/forgot-password/request-otp` | Send password reset OTP                         |
| `POST` | `/api/forgot-password/verify-otp`  | Verify reset OTP                                |
| `POST` | `/api/forgot-password/reset`       | Set new password                                |
| `POST` | `/api/google`                      | Login/register with Google                      |
| `GET`  | `/api/me`                          | Get current user info (requires JWT)            |

### AI Assistant (New)

| Method | Endpoint       | Description                                                |
| ------ | -------------- | ---------------------------------------------------------- |
| `POST` | `/api/ai/chat` | AI Health Assistant with streaming response & data context |

### Dashboard (Doctor)

| Method | Endpoint                                | Description                                               |
| ------ | --------------------------------------- | --------------------------------------------------------- |
| `GET`  | `/api/dashboard/summary`                | Stats: total patients, active count, avg accuracy, trends |
| `GET`  | `/api/patients-with-status`             | All patients with status, progress, last active           |
| `GET`  | `/api/patient/charts/{patient_id}`      | Weekly activity, accuracy trend, muscle focus charts      |
| `GET`  | `/api/overall-stats?user_id=<uid>`      | Aggregate stats for a patient                             |
| `GET`  | `/api/patient/health-metrics/{user_id}` | Heart rate, calories, SpO2, sleep quality                 |
| `GET`  | `/api/patient/health-charts/{user_id}`  | 7-day heart rate & weekly activity chart data             |
| `GET`  | `/api/today-progress`                   | Today's activity for all patients                         |

### Patients

| Method | Endpoint                     | Description                    |
| ------ | ---------------------------- | ------------------------------ |
| `GET`  | `/api/patients`              | List all patients              |
| `GET`  | `/api/patient-sessions/{id}` | Workout sessions for a patient |
| `GET`  | `/api/patient-logs/{id}`     | Exercise logs for a patient    |
| `GET`  | `/api/patient-notes/{id}`    | Doctor notes for a patient     |
| `POST` | `/api/patient-notes`         | Add a note for a patient       |

### Medical Records

| Method | Endpoint                            | Description           |
| ------ | ----------------------------------- | --------------------- |
| `GET`  | `/api/medical-records/{patient_id}` | Get medical record    |
| `PUT`  | `/api/medical-records/{patient_id}` | Update medical record |

### Messaging

| Method | Endpoint        | Description                        |
| ------ | --------------- | ---------------------------------- |
| `GET`  | `/api/messages` | Get conversation with another user |
| `POST` | `/api/messages` | Send a message                     |

### Exercise & Sessions

| Method | Endpoint                             | Description             |
| ------ | ------------------------------------ | ----------------------- |
| `POST` | `/api/workout-sessions`              | Start a workout session |
| `POST` | `/api/session-details`               | Log exercise detail     |
| `GET`  | `/api/weekly-progress?user_id=<uid>` | Recent exercise history |

---

## 🔑 Password Security Rules

All passwords (signup and reset) must satisfy **all 6** of these production-grade rules:

| Rule      | Requirement                                          |
| --------- | ---------------------------------------------------- |
| Length    | Minimum **8** characters                             |
| Length    | Maximum **40** characters                            |
| Uppercase | At least **one** uppercase letter (A-Z)              |
| Lowercase | At least **one** lowercase letter (a-z)              |
| Digit     | At least **one** number (0-9)                        |
| Special   | At least **one** special character (`!@#$%^&*` etc.) |

**Example valid password:** `MyPass1!`

These rules are enforced on **both** the frontend (real-time visual feedback with dim/light indicators) and the **backend** (Pydantic validation returning HTTP 422 with specific error messages).

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

**Current test suite (9 tests, all pass):**

| Test                                        | Description                                          |
| ------------------------------------------- | ---------------------------------------------------- |
| `test_signup_success`                       | Full signup flow: request OTP → verify OTP → get JWT |
| `test_signup_existing_username`             | Rejects duplicate usernames                          |
| `test_signup_existing_email`                | Rejects duplicate emails                             |
| `test_signup_weak_password_no_special_char` | Rejects passwords without special chars              |
| `test_signup_weak_password_too_short`       | Rejects passwords under 8 characters                 |
| `test_login_success`                        | Login with valid credentials returns JWT             |
| `test_login_invalid_password`               | Returns 401 for wrong password                       |
| `test_login_nonexistent_user`               | Returns 401 for unknown email                        |
| `test_google_login_invalid_token`           | Returns 401 for bad Google token                     |

Tests use an **in-memory SQLite** database so they are fully isolated and don't touch production data.

---

## ☁️ Deployment to Vercel

The app is deployed as a **monorepo** on Vercel with two builds:

| Build    | Source                  | Handler                                             |
| -------- | ----------------------- | --------------------------------------------------- |
| Frontend | `frontend/package.json` | `@vercel/static-build` → generates `/frontend/dist` |
| Backend  | `api/index.py`          | `@vercel/python` → serverless function              |

**Deploy command:**

```bash
vercel --prod
```

**Required Vercel environment variables** (set in Vercel project settings):

```
DATABASE_URL
SECRET_KEY
ALGORITHM
SMTP_EMAIL
SMTP_PASSWORD
GOOGLE_CLIENT_ID
VITE_API_BASE_URL=/api
```

> ⚠️ **Important:** The serverless backend cannot write to the filesystem. All logging, file creation, and debug outputs must go to `stdout`/`stderr` only. This is already handled in the codebase.

**What `vercel.json` does:**

- Routes `/api/*` → Python serverless function
- All other routes → Vue SPA (`index.html` for client-side routing)

---

## 🖥 Key UI Pages

| Route               | Component                  | Who can access             |
| ------------------- | -------------------------- | -------------------------- |
| `/`                 | `Login.vue`                | Everyone (unauthenticated) |
| `/doctor`           | `index.vue` (doctor shell) | Doctors only               |
| `/doctor/dashboard` | `Dashboard.vue`            | Doctors                    |
| `/patient`          | `PatientTabs.vue`          | Patients only              |
| `/patient/workout`  | `PatientWorkout.vue`       | Patients                   |
| `/patient/brain`    | `BrainExercise.vue`        | Patients                   |

---

## 👥 Contributors

- Project developed for **COS40005 – Computing Technology Project A**
- Swinburne University of Technology

---

## 📄 License

This project is for academic use at Swinburne University. All rights reserved.
