#!/bin/bash

echo "🚀 Starting Backend (Database-Optional Mode)..."
echo ""
echo "This will start the backend even if database is unavailable."
echo "Camera functionality will work, but data won't be saved."
echo ""

cd /home/tuandat/Documents/September_Semester/Medic1_Le_Minh/backend

# Activate virtual environment
source medic1/bin/activate

# Start backend
uvicorn main:app --reload
