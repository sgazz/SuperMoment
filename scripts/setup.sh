#!/bin/bash

echo "🚀 SuperMoment Setup Script"
echo "=========================="

# Check if virtual environment exists
if [ ! -d "supermoment-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv supermoment-env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source supermoment-env/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup completed!"
echo ""
echo "To start the project:"
echo "1. Backend: cd backend && python main.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or use the start script: ./scripts/start.sh"
