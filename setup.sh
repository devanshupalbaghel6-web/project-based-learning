#!/bin/bash

echo "🚀 Setting up AI-Learn Hub with pyenv and nvm..."

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "❌ pyenv is not installed. Please install pyenv first:"
    echo "   curl https://pyenv.run | bash"
    exit 1
fi

# Check if nvm is installed
if [ ! -d "$HOME/.nvm" ] && ! command -v nvm &> /dev/null; then
    echo "❌ nvm is not installed. Please install nvm first:"
    echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    exit 1
fi

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo ""
echo "🐍 Setting up Python 3.12.2 with pyenv..."

# Install Python 3.12.2 if not already installed
if ! pyenv versions | grep -q "3.12.2"; then
    echo "Installing Python 3.12.2..."
    pyenv install 3.12.2
fi

# Set local Python version
pyenv local 3.12.2
echo "✅ Python 3.12.2 set as local version"

# Verify Python version
python --version

echo ""
echo "📦 Setting up Node.js 20 with nvm..."

# Install and use Node.js 20
nvm install 20
nvm use 20
echo "✅ Node.js 20 activated"

# Verify Node version
node --version
npm --version

# Backend Setup
echo ""
echo "🐍 Setting up Backend..."
cd backend

# Create virtual environment with Python 3.12.2
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your Google Gemini API key."
fi

cd ..

# Frontend Setup
echo ""
echo "📦 Setting up Frontend..."
cd frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created."
fi

cd ..

# Create .nvmrc for Node version
echo "20" > frontend/.nvmrc
echo "✅ Created .nvmrc file"

# Create .python-version for pyenv
echo "3.12.2" > backend/.python-version
echo "✅ Created .python-version file"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update backend/.env with your Google Gemini API key"
echo "   Get your key from: https://makersuite.google.com/app/apikey"
echo "2. Start MongoDB: mongod"
echo "3. Backend: cd backend && source venv/bin/activate && python -m app.main"
echo "4. Frontend: cd frontend && nvm use && npm run dev"
echo ""
echo "🎉 Happy coding!"
