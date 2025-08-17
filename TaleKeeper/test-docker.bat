@echo off
echo Testing Docker installation...
docker --version
if %errorlevel% equ 0 (
    echo ✅ Docker is installed!
    echo Testing Docker functionality...
    docker run hello-world
    if %errorlevel% equ 0 (
        echo ✅ Docker is working properly!
        echo Ready to run: docker-compose up --build
    ) else (
        echo ❌ Docker not working properly
    )
) else (
    echo ❌ Docker not found. Please install Docker Desktop.
)
pause