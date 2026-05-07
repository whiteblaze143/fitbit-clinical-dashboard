#!/bin/bash

# Ensure running from correct directory
cd "$(dirname "$0")"

echo "==========================================="
echo "🏥 Fitbit Clinical Dashboard Startup Script"
echo "==========================================="

echo ""
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt || { echo "Failed to install Python dependencies"; exit 1; }

echo ""
echo "[2/4] Installing Node.js dependencies..."
cd frontend
npm install || { echo "Failed to install Node dependencies"; exit 1; }

echo ""
echo "[3/4] Building Frontend..."
npm run build || { echo "Failed to build frontend"; exit 1; }
cd ..

echo ""
echo "[4/4] Starting FastAPI Server..."
echo "The application will be available at http://localhost:8000"
echo "Press Ctrl+C to stop the server."
echo "==========================================="

# Start the server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
