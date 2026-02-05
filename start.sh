#!/bin/bash

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Please start MongoDB first."
    echo "Run: mongod"
    exit 1
fi

# Ensure correct Python version
cd backend
if [ -f .python-version ]; then
    pyenv local 3.12.2
fi

# Start backend in background
echo "🚀 Starting backend server..."
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend server..."
cd ../frontend

# Use correct Node version
if [ -f .nvmrc ]; then
    nvm use
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "🎉 Both servers are running!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Using:"
echo "  - Python $(python --version 2>&1 | cut -d' ' -f2)"
echo "  - Node $(node --version)"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
