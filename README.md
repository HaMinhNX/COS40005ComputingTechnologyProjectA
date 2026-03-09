# Medic1 - Health & Rehabilitation Platform

Medic1 is a comprehensive platform for health and rehabilitation management, connecting patients with their doctors for personalized exercise plans and progress tracking.

## Tech Stack
- **Frontend**: Vue 3, Vite, TailwindCSS, Pinia (Deployed on Vercel)
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite (Deployed as Serverless Functions)
- **Computer Vision**: MediaPipe for exercise tracking

## Features
- **Authentication**: JWT-based Secure Login & Signup
- **Dashboard**: Doctor and Patient portals with dynamic views
- **Exercise Tracking**: Real-time AI-powered form checking (Squats, Curls, etc.)
- **Communication**: Integrated messaging and scheduling system
- **Deployment-Ready**: Vercel configuration included natively

## Local Development
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
