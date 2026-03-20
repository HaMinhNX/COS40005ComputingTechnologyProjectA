#!/bin/bash

echo "🚀 Starting Backend (Medic1 Rehabilitation API)..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment (check standard names)
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../.venv" ]; then
    # In case script is run from a subfolder although we cd'd above
    source ../.venv/bin/activate
fi

# Start backend on port 8001
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

