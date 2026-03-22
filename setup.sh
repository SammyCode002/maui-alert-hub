#!/bin/bash
# ============================================================
# Maui Alert Hub - Quick Setup Script
# Run this once after cloning to get everything ready.
# Usage: bash setup.sh
# ============================================================

set -e

echo "🌊 Setting up Maui Alert Hub..."
echo ""

# --- Backend Setup ---
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -r requirements.txt -q

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "  Creating .env from .env.example..."
    cp .env.example .env
fi

echo "  Backend ready!"
cd ..

# --- Frontend Setup ---
echo ""
echo "📦 Setting up frontend..."
cd frontend

# Install npm dependencies
echo "  Installing npm dependencies..."
npm install --silent

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "  Creating .env from .env.example..."
    cp .env.example .env
fi

echo "  Frontend ready!"
cd ..

# --- Done ---
echo ""
echo "============================================"
echo "  Maui Alert Hub is ready!"
echo "============================================"
echo ""
echo "  Start the backend:"
echo "    cd backend && source venv/bin/activate"
echo "    uvicorn app.main:app --reload --port 8000"
echo ""
echo "  Start the frontend (new terminal):"
echo "    cd frontend && npm run dev"
echo ""
echo "  Then open: http://localhost:5173"
echo "  API docs:  http://localhost:8000/docs"
echo ""
echo "🤙 Aloha! Happy coding!"
