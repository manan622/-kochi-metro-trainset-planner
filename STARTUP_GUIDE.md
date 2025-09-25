# Kochi Metro Trainset Planner - Startup Guide

This guide explains the different ways to start the development environment for the Kochi Metro Trainset Induction Planner.

## 🚀 Quick Start Options

### 1. Windows Batch Script (Easiest for Windows users)
- **File**: `start-dev.bat`
- **How to use**: Double-click the file or run it from Command Prompt
- **What it does**: Starts both backend and frontend servers in separate command windows

### 2. Python Script (Cross-platform)
- **File**: `start-dev.py`
- **How to use**: Run `python start-dev.py` from the project root
- **What it does**: Starts both servers and manages them in a single terminal window

### 3. Node.js Script (Cross-platform)
- **File**: `start-dev.js`
- **How to use**: Run `node start-dev.js` from the project root
- **What it does**: Starts both frontend and backend servers using Node.js child processes

### 4. NPM Dev Script (Cross-platform)
- **File**: Uses the script defined in `frontend/package.json`
- **How to use**: 
  1. Navigate to the `frontend` directory
  2. Run `npm run dev`
- **What it does**: Starts both frontend and backend servers using `concurrently`

### 4. Shell Script (Mac/Linux)
- **File**: `start-dev.sh`
- **How to use**: Run `./start-dev.sh` from the project root (may need to make it executable first)
- **What it does**: Starts both servers and manages them in a single terminal window

## 📋 Prerequisites

Before starting the development environment, ensure you have:

1. **Python 3.10+** installed
2. **Node.js 18+** installed
3. **PostgreSQL** running (can be started via Docker)
4. All dependencies installed:
   - Backend: `pip install -r backend/requirements.txt`
   - Frontend: `cd frontend && npm install`

## 🔧 Server Details

- **Backend**: Runs on `http://localhost:8001`
- **Frontend**: Runs on `http://localhost:3000`
- **API Documentation**: Available at `http://localhost:8001/docs`

## 🛑 Stopping the Servers

- **Batch script**: Close the command windows or press Ctrl+C
- **Python script**: Press Ctrl+C in the terminal
- **NPM script**: Press Ctrl+C in the terminal
- **Shell script**: Press Ctrl+C in the terminal

## 🐛 Troubleshooting

### Common Issues:

1. **Port already in use**:
   - Make sure no other instances are running
   - Change the port numbers in the startup scripts if needed

2. **Dependencies not found**:
   - Ensure all requirements are installed
   - Check that you're in the correct directory

3. **Permission errors**:
   - On Mac/Linux, make scripts executable: `chmod +x start-dev.sh`

4. **Database connection errors**:
   - Ensure PostgreSQL is running
   - Check database credentials in the `.env` file

### Logs:

- **Backend logs**: Check the terminal where the backend was started
- **Frontend logs**: Check the terminal where the frontend was started
- **Batch script logs**: Check the separate command windows
- **Python/shell script logs**: Check the main terminal window

## 🎯 Recommended Workflow

1. Start the database: `docker run -d --name postgres -e POSTGRES_DB=kochi_metro_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15`
2. Run database migrations: `cd backend && alembic upgrade head`
3. Generate sample data: `cd backend && python -c "from app.utils.csv_importer import generate_sample_data_command; generate_sample_data_command()"`
4. Start the development servers using one of the methods above
5. Access the application at `http://localhost:3000`

## 📝 Notes

- The frontend automatically proxies API requests to the backend
- Changes to code will automatically reload the servers (hot reloading)
- The startup scripts will automatically terminate both servers when stopped