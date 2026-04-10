# HaminG — Technical Documentation

> This document is intended for developers and contributors. It covers the internal architecture, data flows, component design, and development patterns used throughout the codebase.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Authentication & Security](#2-authentication--security)
3. [Backend Deep Dive](#3-backend-deep-dive)
4. [Frontend Deep Dive](#4-frontend-deep-dive)
5. [Database Models Reference](#5-database-models-reference)
6. [Password Validation Rules](#6-password-validation-rules)
7. [Doctor Dashboard](#7-doctor-dashboard)
8. [Patient Dashboard](#8-patient-dashboard)
9. [Exercise System](#9-exercise-system)
10. [Messaging System](#10-messaging-system)
11. [Email & OTP System](#11-email--otp-system)
12. [Vercel Deployment Guide](#12-vercel-deployment-guide)
13. [Testing Guide](#13-testing-guide)
14. [Common Pitfalls & Known Issues](#14-common-pitfalls--known-issues)

---

## 1. System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Vercel Platform                        │
│                                                           │
│  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │   Vue 3 SPA          │  │  FastAPI Serverless       │  │
│  │   (/frontend/dist)   │  │  (/api/index.py)          │  │
│  │                      │  │                           │  │
│  │  - Vue Router        │  │  - JWT Auth               │  │
│  │  - D3.js charts      │  │  - Pydantic validation    │  │
│  │  - Lucide icons      │  │  - SQLAlchemy ORM         │  │
│  │  - TailwindCSS       │  │  - bcrypt hashing         │  │
│  └──────────┬───────────┘  └──────────┬───────────────┘  │
│             │ /api/*                   │                   │
│             └─────────────────────────┘                   │
└──────────────────────────────────────────────────────────┘
                                │ DATABASE_URL (env)
                                ▼
                     ┌────────────────────┐
                     │   PostgreSQL        │
                     │  (Neon / Supabase) │
                     └────────────────────┘
```

### Request Lifecycle

1. User makes an action (e.g., login button click)
2. Vue component calls `fetch(API_BASE_URL + '/login', {...})`
3. Vercel edge routes `/api/*` to the Python serverless function
4. `api/index.py` (a thin wrapper) imports and runs the FastAPI `app`
5. FastAPI validates the request body with Pydantic
6. The router handler runs business logic and queries PostgreSQL
7. Response JSON is returned to the Vue component
8. Vue updates reactive state → UI re-renders

### Configuration

**Frontend** (`frontend/src/config.js`):

```js
// In production (Vercel), VITE_API_BASE_URL = "/api" (set in vercel.json env)
// In development, falls back to http://localhost:8001/api
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8001/api";
```

**Backend** (`backend/.env`):

```
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALGORITHM=HS256
SMTP_EMAIL=...
SMTP_PASSWORD=...
GOOGLE_CLIENT_ID=...
```

---

## 2. Authentication & Security

### JWT Flow

```
Client                          Server
  │                               │
  │  POST /api/login              │
  │  { username, password }       │
  │ ─────────────────────────────>│
  │                               │ 1. Lookup user by email
  │                               │ 2. bcrypt.verify(password, hash)
  │                               │ 3. create_access_token(sub=user_id, role=role)
  │  { access_token, user_id,     │
  │    role, full_name, ... }      │
  │ <─────────────────────────────│
  │                               │
  │  GET /api/patients            │
  │  Authorization: Bearer <jwt>  │
  │ ─────────────────────────────>│
  │                               │ 4. dependencies.get_current_user()
  │                               │    - decode JWT
  │                               │    - look up User in DB
  │                               │    - inject into endpoint handler
  │  [patient list]               │
  │ <─────────────────────────────│
```

### Token Storage

Tokens are stored in `localStorage` on the client:

```js
localStorage.setItem("token", data.access_token);
localStorage.setItem("user", JSON.stringify({ user_id, role, full_name }));
```

Every API call reads it:

```js
const token = localStorage.getItem("token");
fetch(url, { headers: { Authorization: `Bearer ${token}` } });
```

### Password Hashing

Uses `passlib` with bcrypt:

```python
# backend/auth.py
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### Role-Based Access

Two roles exist: `doctor` and `patient`. The `get_current_user` dependency in `dependencies.py` validates the JWT and returns the `User` model. Specific endpoints use `get_current_doctor` or `get_current_patient` to enforce role access.

---

## 3. Backend Deep Dive

### Directory Structure

```
backend/
├── main.py          ← FastAPI app creation, middleware, lifespan, exception handlers
├── database.py      ← SQLAlchemy engine, SessionLocal, Base, get_db()
├── models.py        ← All SQLAlchemy ORM models
├── auth.py          ← JWT creation (create_access_token), password utils
├── dependencies.py  ← get_current_user, get_current_doctor, get_current_patient
├── enums.py         ← Python enums: UserRole, PatientStatus, etc.
├── exceptions.py    ← Custom exception classes
├── schemas/         ← Pydantic request/response schemas
│   ├── __init__.py  ← Re-exports all schemas (keeps imports clean in routers)
│   ├── user.py      ← UserCreate, UserLogin, ResetPassword, etc.
│   ├── exercise.py  ← Session, log schemas
│   ├── medical.py   ← MedicalRecord schemas
│   └── communication.py ← Message, notification schemas
└── routers/         ← One file per feature domain
```

### AI Assistant Ethical Policy (Role-Based)

The AI assistant is shared by doctors and patients, but it must behave differently by role to satisfy safety and ethics constraints.

**Implementation references:**

- Backend prompt policy: `backend/routers/ai_chat.py`
- Frontend UI entry point: `frontend/src/components/AIChatbox.vue`

#### Patient Mode (`role=patient`)

**Allowed**

- Explain and summarize the patient’s own rehab/workout data (attendance, trends, reps, completed sessions).
- Encourage adherence to the existing plan assigned by clinicians.
- Provide safe, non-prescriptive guidance (e.g. “contact your doctor” when warning signs appear).
- Help the patient prepare questions for their doctor based on the logged data.

**Disallowed (hard safety boundaries)**

- Do **not** prescribe or suggest specific exercises, reps, frequency, intensity, or create any “assignment” plan.
- Do **not** recommend changing the treatment/exercise plan.
- Do **not** present the system’s supported exercise library as options for the patient to self-select.
- Do **not** diagnose conditions or provide medication advice.

#### Doctor Mode (`role=doctor`)

**Allowed**

- Summarize and analyze patient data and trends with explicit reasoning grounded in the provided context.
- Suggest exercise assignments **only** from the system’s supported exercise library (no novel exercise creation).
- Draft messages or clinical summaries for doctor review (human-in-the-loop).

**Ethical constraints still apply**

- If data is missing or uncertain, the AI must say so (avoid hallucination).
- Never reveal information about other patients.
- Recommendations are advisory; the clinician remains responsible for final decisions.

### Router Pattern

Each router follows the same pattern:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["my-feature"])

@router.get("/my-endpoint")
async def my_handler(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # business logic here
    return {"result": "..."}
```

### Pydantic Validation

All request bodies are Pydantic models. Validation errors return `HTTP 422` with a `detail` array that the frontend's `getErrorMessage()` translates to Vietnamese.

**Password validation** is centralized in `schemas/user.py`:

```python
def validate_password_strength(v: str) -> str:
    if len(v) < 8:           raise ValueError('...')
    if len(v) > 40:          raise ValueError('...')
    if not any(c.isupper()): raise ValueError('...')
    if not any(c.islower()): raise ValueError('...')
    if not any(c.isdigit()): raise ValueError('...')
    if not SPECIAL_CHAR_REGEX.search(v): raise ValueError('...')
    return v
```

### Database Connection

```python
# backend/database.py
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")

# Vercel serverless: use StaticPool for SQLite, connection pool for PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
```

---

## 4. Frontend Deep Dive

### Component Architecture

```
index.vue (app shell)
├── Dashboard.vue          ← Doctor: patient list + detail panel
│   └── (inline charts via D3.js)
├── DoctorPatientDetail.vue ← Tabbed patient view
│   └── PatientDashboard.vue ← Patient health overview
├── Assignment.vue         ← Exercise assignment wizard
├── Scheduling.vue         ← Calendar-based scheduling
├── DoctorMessaging.vue    ← Chat UI (doctor side)
├── PatientTabs.vue        ← Patient app shell
│   ├── PatientWorkout.vue     ← AI-guided exercise
│   ├── BrainExercise.vue      ← Cognitive games
│   ├── PatientScheduling.vue  ← View appointments
│   └── PatientMessaging.vue   ← Chat UI (patient side)
└── Login.vue              ← Auth forms
```

### Vue 3 Patterns Used

**Composition API (script setup):**

```vue
<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
const data = ref([])
const filtered = computed(() => data.value.filter(...))
onMounted(() => loadData())
</script>
```

**D3.js Integration (charts):**
D3 manipulates SVG elements via `ref()` on a container `<div>`. When `nextTick()` resolves, the container has been mounted and D3 can safely measure its dimensions:

```js
const chartEl = ref(null)
nextTick(() => {
  const width = chartEl.value.clientWidth
  const svg = d3.select(chartEl.value).append('svg').attr('width', width)...
})
```

### Router Guards

```js
// router.js
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  if (to.meta.requiresAuth && !token) return next("/");
  if (to.meta.role && user.role !== to.meta.role) return next("/");
  next();
});
```

### State Management

No Vuex/Pinia — state is managed locally within each component using `ref()` and `computed()`. Data flows from parent → child via props, and from child → parent via `$emit`. Shared state (like the logged-in user) is stored in `localStorage` and read at component mount.

---

## 5. Database Models Reference

### `users`

| Column           | Type        | Notes                                 |
| ---------------- | ----------- | ------------------------------------- |
| `user_id`        | UUID        | Primary key                           |
| `username`       | String(50)  | Unique                                |
| `email`          | String(100) | Unique, indexed                       |
| `password_hash`  | String(255) | bcrypt hash                           |
| `full_name`      | String(100) |                                       |
| `role`           | String(20)  | `'doctor'` or `'patient'`             |
| `status`         | String(20)  | `active / needs_attention / inactive` |
| `last_active_at` | DateTime TZ | Updated on workout                    |
| `created_at`     | DateTime TZ | Auto                                  |

### `workout_sessions`

| Column       | Type        | Notes                     |
| ------------ | ----------- | ------------------------- |
| `session_id` | UUID        | Primary key               |
| `user_id`    | UUID FK     | → users                   |
| `start_time` | DateTime TZ | Auto                      |
| `end_time`   | DateTime TZ | Set on completion         |
| `status`     | String(20)  | `in_progress / completed` |

### `session_details`

One row per exercise within a session:

| Column             | Type         | Notes                          |
| ------------------ | ------------ | ------------------------------ |
| `detail_id`        | Integer PK   |                                |
| `session_id`       | UUID FK      | → workout_sessions             |
| `exercise_type`    | String(50)   | e.g., `'squat'`, `'arm_raise'` |
| `reps_completed`   | Integer      |                                |
| `duration_seconds` | Integer      |                                |
| `accuracy_score`   | Numeric(5,2) | 0–100                          |
| `completed_at`     | DateTime TZ  | Auto                           |

### `otp_verifications`

Temporary records, deleted after use:

| Column       | Type        | Notes                                                |
| ------------ | ----------- | ---------------------------------------------------- |
| `email`      | String(100) | Unique                                               |
| `otp_code`   | String(6)   | Random 6-digit code                                  |
| `expires_at` | DateTime TZ | 15 minutes from creation                             |
| `user_data`  | Text        | JSON: signup data or `{"reason": "forgot_password"}` |

---

## 6. Password Validation Rules

Enforced on both frontend and backend:

| #   | Rule              | Regex / Check                    |
| --- | ----------------- | -------------------------------- | ----------- |
| 1   | Min 8 characters  | `len(v) >= 8`                    |
| 2   | Max 40 characters | `len(v) <= 40`                   |
| 3   | Uppercase letter  | `/[A-Z]/`                        |
| 4   | Lowercase letter  | `/[a-z]/`                        |
| 5   | Digit             | `/[0-9]/`                        |
| 6   | Special character | `/[!@#$%^&\*()\-\_=+\[\]{};':"\\ | ,.<>/?`~]/` |

**Frontend** — `Login.vue` checks in real-time via `checkPasswordStrength()` and displays a panel of 6 rules that dim (grey, opacity 0.6) when unmet and light up green with a `✓` when met. The submit button is `disabled` until all 6 rules pass AND both password fields match.

**Backend** — `validate_password_strength()` in `schemas/user.py` is called by every password-accepting Pydantic schema's `@field_validator`. Returns HTTP 422 on failure with a specific Vietnamese-translated error message.

---

## 7. Doctor Dashboard

### Patient List

- Fetches from `GET /api/patients-with-status`
- Displays a **numbered list** (`#1`, `#2`, ...) so doctors can see total count at a glance
- Search filters by name or email (client-side)
- Status badge: `Hoạt động` (green), `Cần chú ý` (orange), `Không hoạt động` (grey)

### Patient Detail Panel (Overview Tab)

When a doctor clicks a patient, the right panel loads data from **3 APIs in parallel**:

```js
Promise.all([
  fetch(`/api/patient-sessions/${id}`),
  fetch(`/api/patient-logs/${id}`),
  fetch(`/api/patient-notes/${id}`),
  fetch(`/api/patient/charts/${id}`), // ← weekly activity + accuracy + exercise dist
  fetch(`/api/overall-stats?user_id=${id}`), // ← total reps, sessions, days
]);
```

**4 Quick Stats Cards:**

- Total Reps (from `overall-stats`)
- Total Sessions (from `overall-stats`)
- Avg Accuracy % (calculated from logs)
- Active Days (from `overall-stats`)

**Weekly Activity Bar Chart:**

- Data: `GET /api/patient/charts/{id}` → `weekly_activity: [{date, reps}]`
- 7 bars, one per day, height proportional to reps
- Labels: day abbreviations (CN, T2, T3...)

**Accuracy Trend Line Chart (D3.js):**

- Data: `GET /api/patient/charts/{id}` → `accuracy_trend: [{date, score}]`
- SVG line chart with gradient area fill
- Y-axis: 0–100%, X-axis: dates
- Grid lines at 0, 25, 50, 75, 100

**Exercise Distribution:**

- Data: `GET /api/patient/charts/{id}` → `muscle_focus: [{exercise_type, count}]`
- Horizontal progress bars, each a different colour
- Shows exercise name, count, and percentage

### Dashboard Stats (Top Row)

Fetched from `GET /api/dashboard/summary`:

- **Total patients** — DB count of all users with `role='patient'`
- **Active** — patients with workout in last 7 days
- **Needs attention** — patients with workout 3–7 days ago but not recent
- **Avg form score** — average `accuracy_score` across all `session_details`

---

## 8. Patient Dashboard

`PatientDashboard.vue` uses the patient's own `user_id` (from localStorage) to fetch:

| Endpoint                                    | Data shown                                |
| ------------------------------------------- | ----------------------------------------- |
| `GET /api/patient/health-metrics/{user_id}` | Heart rate, calories, SpO2, sleep quality |
| `GET /api/patient/health-charts/{user_id}`  | 7-day HR trend, weekly rep chart          |
| `GET /api/overall-stats?user_id={id}`       | Total reps, sessions, days                |

**Health metrics are logically derived** from real workout data (not mock):

- Calories = base BMR + (reps × 5) + (duration × 0.1)
- Resting HR = base − (days_active × 0.5), floor 50
- SpO2 = 96–99, improves with overall fitness
- Sleep quality = 75 baseline ± activity bonus/penalty

---

## 9. Exercise System

### Physical Exercise (`PatientWorkout.vue`)

1. Patient selects an exercise from their assignments
2. Camera opens, MediaPipe pose detection runs in the browser
3. `exercise_logic.py` defines rep counting and form scoring logic per exercise type
4. On completion, `POST /api/session-details` saves the results

### Brain Exercise (`BrainExercise.vue`)

- Multiple cognitive mini-games (memory, arithmetic, pattern recognition)
- Results saved to `brain_exercise_sessions` and `brain_exercise_logs`

### Exercise Assignment Flow

1. Doctor creates a combo (group of exercises) or picks individual exercises
2. Doctor assigns to a patient via `POST /api/assignments`
3. Patient sees assignments in their workout tab
4. Doctor tracks completion via the dashboard

---

## 10. Messaging System

- `GET /api/messages?other_user_id={id}` — fetch conversation
- `POST /api/messages` — send message `{ receiver_id, content }`
- Messages are stored in the `messages` table with `sender_id`, `receiver_id`, `content`, `is_read`
- UI polls or uses optimistic updates (message appears immediately on send)

**Important (Vercel serverless):** The messaging endpoint reads `current_user` from the JWT directly — it does **not** read from the filesystem. This was a bug fix in a previous version.

---

## 11. Email & OTP System

### Signup Flow

```
1. POST /api/signup/request-otp
   → Validates all user data (including password strength)
   → Generates 6-digit OTP
   → Stores in otp_verifications with 15min expiry
   → Sends email via Gmail SMTP
   → Returns 200 {message}

2. POST /api/signup/verify-otp
   → Looks up OTP record by email
   → Checks code matches and not expired
   → Creates User in DB
   → Deletes OTP record
   → Returns JWT token (user is logged in immediately)
```

### Forgot Password Flow

```
1. POST /api/forgot-password/request-otp
   → Checks user exists with that email
   → Generates OTP, stores with reason="forgot_password"
   → Sends email

2. POST /api/forgot-password/verify-otp
   → Validates OTP (doesn't delete yet)
   → Returns 200 {message: "Mã OTP hợp lệ"}

3. POST /api/forgot-password/reset
   → Re-validates OTP (security check)
   → Validates new password strength
   → Updates user.password_hash with new bcrypt hash
   → Deletes OTP record
```

### SMTP Configuration

Uses `smtplib.SMTP_SSL('smtp.gmail.com', 465)` with Gmail App Password. If `SMTP_EMAIL` or `SMTP_PASSWORD` env vars are missing, it prints the OTP to the server log (useful for local development).

---

## 12. Vercel Deployment Guide

### Structure Required by Vercel

```
/
├── api/
│   └── index.py      ← MUST be here — Vercel Python serverless
├── frontend/
│   ├── package.json  ← Vercel runs: npm run build
│   └── dist/         ← Generated by the build
└── vercel.json       ← Routing configuration
```

### `api/index.py`

This file is the serverless entry point. It imports the FastAPI app:

```python
from backend.main import app  # or however it's structured
```

### Environment Variables in Vercel

Set these in **Vercel Project Settings → Environment Variables**:

```
DATABASE_URL         postgresql://user:pass@host/db
SECRET_KEY           your-long-random-secret
ALGORITHM            HS256
SMTP_EMAIL           yourmail@gmail.com
SMTP_PASSWORD        your-app-password
GOOGLE_CLIENT_ID     your-client-id.apps.googleusercontent.com
VITE_API_BASE_URL    /api
```

### Database for Production

Use a serverless-compatible PostgreSQL:

- **[Neon](https://neon.tech)** (recommended, free tier available)
- **[Supabase](https://supabase.com)** (also has free tier)

Both provide a `postgresql://...` connection string.

### Deploying

```bash
# From project root, after committing changes:
vercel --prod
```

Or configure Vercel to auto-deploy from your GitHub branch by linking the repo in the Vercel dashboard.

---

## 13. Testing Guide

Tests live in `backend/tests/test_auth_endpoints.py`.

### Running Tests

```bash
cd backend
pytest tests/ -v          # Verbose output
pytest tests/ -v -x       # Stop on first failure
pytest tests/ -k "login"  # Run only tests matching "login"
```

### Test Setup

Tests override the database with an in-memory SQLite instance so they never touch production:

```python
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)
app.dependency_overrides[get_db] = override_get_db  # inject test DB
```

### Adding New Tests

Follow the existing pattern:

```python
def test_my_new_feature():
    response = client.post("/api/my-endpoint", json={...})
    assert response.status_code == 200
    assert response.json()["key"] == "expected_value"
```

---

## 14. Common Pitfalls & Known Issues

### Datetime Timezone Awareness

SQLite returns timezone-naive datetimes while PostgreSQL returns timezone-aware ones. The codebase handles this:

```python
expires = verify_record.expires_at
if expires.tzinfo is None:
    expires = expires.replace(tzinfo=timezone.utc)
```

### Vercel Filesystem is Read-Only

You **cannot** write files in Vercel serverless functions. All previous debug logging to files has been removed. Use `print()` or `logging.info()` which go to Vercel's log viewer.

### CORS

The backend only allows requests from specific origins (see `main.py`). If you add a new domain, add it to the `origins` list.

### Google OAuth in Production

`GOOGLE_CLIENT_ID` must be set in Vercel env vars. The OAuth redirect must be registered in Google Cloud Console for your production domain.

### JWT Token Expiry

Default token expiry is set in `auth.py`. Expired tokens return 401. The frontend does not currently auto-refresh tokens — users must log in again.

### Password Validator Duplicate Bug (Fixed)

The old `schemas/user.py` had two `@field_validator('password')` methods in `ResetPassword` (one was named incorrectly). Python silently used only the last one. This is fixed — all schemas now call the shared `validate_password_strength()` function.
