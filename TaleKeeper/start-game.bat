@echo off
cls
echo =========================================
echo        D^&D 2024 TaleKeeper
echo         Game Startup Script
echo =========================================
echo.

REM Set the script directory as working directory
cd /d "%~dp0"

echo [INFO] Checking system requirements...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo [OK] Python is installed

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Node.js is installed

REM Check if Docker is available (optional)
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker is available
    set DOCKER_AVAILABLE=true
) else (
    echo [INFO] Docker not found - will use local development mode
    set DOCKER_AVAILABLE=false
)

echo.
echo Choose startup option:
echo 1. Start with Docker (Full stack with PostgreSQL)
echo 2. Start Local Development (SQLite + direct Python/Node)
echo 3. Backend Only (API server only)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto docker_start
if "%choice%"=="2" goto local_start
if "%choice%"=="3" goto backend_only
if "%choice%"=="4" goto exit
echo Invalid choice. Defaulting to local development.

:local_start
echo.
echo =========================================
echo   Starting Local Development Mode
echo =========================================
echo.

REM Ensure we're using SQLite in .env
echo [INFO] Configuring for SQLite database...
echo [INFO] Creating .env file for local development...
(
    echo POSTGRES_DB=dnd_game
    echo POSTGRES_USER=dnd_admin
    echo POSTGRES_PASSWORD=secure_password_change_me
    echo DATABASE_URL=sqlite:///./talekeeper.db
    echo REACT_APP_API_URL=http://localhost:8000
) > .env

REM Install backend dependencies
echo [INFO] Installing backend dependencies...
cd backend
if not exist venv (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing Python packages...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)

echo [OK] Backend dependencies installed

REM Test database setup
echo [INFO] Setting up database...
python -c "from database import init_db; init_db(); print('[OK] Database initialized')"
if %errorlevel% neq 0 (
    echo [ERROR] Database setup failed
    pause
    exit /b 1
)

REM Install frontend dependencies
echo [INFO] Installing frontend dependencies...
cd ..\frontend
if not exist node_modules (
    echo [INFO] Running npm install...
    npm install >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

echo [OK] Frontend dependencies installed

REM Start backend in background
echo [INFO] Starting backend server...
cd ..\backend
start "TaleKeeper Backend" cmd /k "call venv\Scripts\activate.bat && python main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Test backend
echo [INFO] Testing backend connection...
timeout /t 2 /nobreak >nul
python -c "
import requests
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.status_code == 200:
        print('[OK] Backend is responding')
    else:
        print('[WARNING] Backend health check failed')
except:
    print('[WARNING] Backend may still be starting...')
" 2>nul

REM Start frontend
echo [INFO] Starting frontend...
cd ..\frontend
echo.
echo =========================================
echo   Game is starting!
echo =========================================
echo.
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo The game will open in your browser shortly...
echo Press Ctrl+C in either window to stop the servers.
echo.

npm start

goto end

:docker_start
echo.
echo =========================================
echo      Starting with Docker
echo =========================================
echo.

if "%DOCKER_AVAILABLE%"=="false" (
    echo [ERROR] Docker is not available
    echo Please install Docker Desktop from https://docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Ensure we're using PostgreSQL in .env for Docker
echo [INFO] Configuring for PostgreSQL database...
echo [INFO] Creating .env file for Docker mode...
(
    echo POSTGRES_DB=dnd_game
    echo POSTGRES_USER=dnd_admin
    echo POSTGRES_PASSWORD=secure_password_change_me
    echo DATABASE_URL=postgresql://dnd_admin:secure_password_change_me@db:5432/dnd_game
    echo REACT_APP_API_URL=http://localhost:8000
) > .env

echo [INFO] Starting Docker containers...
echo This may take a few minutes on first run...
echo.

docker-compose up --build
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker startup failed!
    echo.
    echo Try running: fix-docker.bat to clean up Docker issues
    echo Or select option 2 for Local Development mode
    echo.
    pause
)

goto end

:backend_only
echo.
echo =========================================
echo     Starting Backend Only
echo =========================================
echo.

REM Use SQLite for backend only mode
echo [INFO] Configuring for SQLite database...
if not exist .env (
    (
        echo POSTGRES_DB=dnd_game
        echo POSTGRES_USER=dnd_admin
        echo POSTGRES_PASSWORD=secure_password_change_me
        echo DATABASE_URL=sqlite:///./talekeeper.db
        echo REACT_APP_API_URL=http://localhost:8000
    ) > .env
)

cd backend
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

echo [INFO] Starting backend server...
echo.
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.

python main.py

goto end

:exit
echo Goodbye!
exit /b 0

:end
echo.
echo =========================================
echo      TaleKeeper Shutdown
echo =========================================
echo.
pause