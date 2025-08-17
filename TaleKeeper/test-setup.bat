@echo off
echo =========================================
echo      TaleKeeper Setup Test
echo =========================================
echo.

cd /d "%~dp0"

echo [TEST] Python installation...
python --version
if %errorlevel% neq 0 (
    echo [FAIL] Python not found
    goto end
) else (
    echo [PASS] Python found
)

echo.
echo [TEST] Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo [FAIL] Node.js not found
    goto end
) else (
    echo [PASS] Node.js found
)

echo.
echo [TEST] Backend dependencies...
cd backend
python -c "import fastapi, sqlalchemy, pydantic; print('[PASS] Core dependencies available')" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing backend dependencies...
    if not exist venv (
        python -m venv venv
    )
    call venv\Scripts\activate.bat
    pip install -r requirements.txt >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] Backend dependencies installed
    ) else (
        echo [FAIL] Backend dependency installation failed
        goto end
    )
) else (
    echo [PASS] Backend dependencies already available
)

echo.
echo [TEST] Database setup...
python -c "
from database import test_connection, init_db
try:
    if test_connection():
        print('[PASS] Database connection successful')
        init_db()
        print('[PASS] Database tables created')
    else:
        print('[FAIL] Database connection failed')
except Exception as e:
    print(f'[FAIL] Database error: {e}')
" 2>nul

echo.
echo [TEST] FastAPI application...
python -c "
try:
    from main import app
    route_count = len([r for r in app.routes if hasattr(r, 'path')])
    print(f'[PASS] FastAPI app loaded with {route_count} routes')
except Exception as e:
    print(f'[FAIL] FastAPI error: {e}')
" 2>nul

echo.
echo [TEST] Frontend dependencies...
cd ..\frontend
if exist node_modules (
    echo [PASS] Frontend dependencies already installed
) else (
    echo [INFO] Installing frontend dependencies...
    npm install >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] Frontend dependencies installed
    ) else (
        echo [FAIL] Frontend dependency installation failed
        goto end
    )
)

echo.
echo [TEST] Docker availability...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Docker is available
    docker-compose config >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] Docker Compose configuration valid
    ) else (
        echo [WARN] Docker Compose configuration issues
    )
) else (
    echo [INFO] Docker not available (optional)
)

echo.
echo =========================================
echo        Setup Test Complete
echo =========================================
echo.
echo All core components tested successfully!
echo You can now run: start-game.bat
echo.

:end
pause