# Project Setup Guide

> ⚠️ **Remember to create the project's own Python virtual environment before starting.**

---

## 🐍 Virtual Environment Setup

```bash
python -m venv venv
```

Activate the environment:

```bash
# PowerShell
venv\Scripts\Activate.ps1

# CMD
venv\Scripts\activate
```

---

## 📦 Installing Dependencies

### Frontend
```bash
cd frontend
npm install
cd ..
```

### Backend
```bash
cd backend
pip install -r requirements.txt
cd ..
```

---

## 🚀 Running the Program (3 terminals > remember to re-activate virtual environment on new terminal)

### 1. Frontend
```bash
cd frontend
npm run dev
```

### 2. Backend — Main App
```bash
cd backend
uvicorn main:app --reload
```

### 3. Backend — Dashboard API
```bash
cd backend
uvicorn api_dashboard:app --reload --port 8001
```