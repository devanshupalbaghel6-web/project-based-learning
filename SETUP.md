# Development Scripts

This directory contains utility scripts for development.

## Setup Script (`setup.sh`)

Installs all dependencies for both frontend and backend.

```bash
chmod +x setup.sh
./setup.sh
```

## Start Script (`start.sh`)

Starts both frontend and backend servers simultaneously.

```bash
chmod +x start.sh
./start.sh
```

## Manual Commands

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```
