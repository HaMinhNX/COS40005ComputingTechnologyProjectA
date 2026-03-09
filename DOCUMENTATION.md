# Medic1 Core Documentation (For Future LLM Agents)

This document provides a comprehensive overview of the Medic1 application architecture, the recent fixes applied, and the deployment setup on Vercel. This is intended for developer handoff or future AI agent context.

## 1. System Architecture

The application is split into two main components:

### Frontend
- **Framework**: Vue 3 with Vite.
- **State Management**: Pinia.
- **Routing**: Vue Router.
- **Styling**: Tailwind CSS & plain CSS (in `assets/`).
- **Computer Vision**: Uses `@mediapipe/tasks-vision` for real-time exercise form tracking.
- **Location**: `frontend/`

### Backend
- **Framework**: FastAPI (Python).
- **ORM**: SQLAlchemy.
- **Database**: PostgreSQL (NeonDB by default) / SQLite.
- **Authentication**: JWT parsing via `python-jose` and password hashing via `passlib/bcrypt` (Note: Pydantic V2 validations are in place).
- **Location**: `backend/`

## 2. Recent Audit and Fixes (March 2026)

During a deep long-horizon audit, several actions were taken to bring the codebase to a production-ready state with zero warnings:

1. **SQLAlchemy Deprecation Fixes**:
   - Updated `declarative_base` import in `database.py` from `sqlalchemy.ext.declarative` to `sqlalchemy.orm`.
2. **FastAPI Lifespan Fixes**:
   - Replaced deprecated `@app.on_event("startup")` with the asynchronous `lifespan` context manager in `main.py`.
3. **Pydantic V2 Migration**:
   - Upgraded `@validator` to `@field_validator` and marked them as `@classmethod` across all schemas (`user.py`, `exercise.py`, `communication.py`).
   - Replaced legacy `class Config: from_attributes = True` with `model_config = {"from_attributes": True}` across all response schemas.
   - Replaced `min_items` with `min_length` in list validations.
4. **Timezone Fixes**:
   - Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)` for JWT token expiration calculation in `auth.py`.

*Result: 0 errors and 0 warnings during Pytest execution.*

## 3. Vercel Deployment Configuration

The app uses a monorepo setup configured for Vercel, mapped via `vercel.json` in the root:

```json
{
  "version": 2,
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/vite" },
    { "src": "api/index.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/index.py" },
    { "src": "/(.*)", "dest": "/frontend/$1" }
  ]
}
```

- **`api/index.py`**: This is a required Vercel Serverless Function entry point. It simply imports the FastAPI `app` from `backend.main`.
- **Environment Variables**:
  Make sure `SECRET_KEY`, `DATABASE_URL` are mapped properly inside Vercel's Environment Variables panel.

## 4. Next Steps for Maintainers
- Keep monitoring the MediaPipe task pipeline performance on low-end devices.
- Maintain the PostgreSQL connection pool limit (currently size 5, overflow 10) carefully with Vercel's Serverless environment where connections spin up dynamically. 
- You can find the automated Vercel preview/production links in the dashboard.
