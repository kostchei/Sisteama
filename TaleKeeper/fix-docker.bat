@echo off
echo =========================================
echo      Docker Cleanup and Fix
echo =========================================
echo.

echo [INFO] Stopping any running containers...
docker-compose down -v

echo [INFO] Cleaning up Docker images...
docker system prune -f

echo [INFO] Removing any corrupted TaleKeeper images...
docker rmi talekeeper-frontend 2>nul
docker rmi talekeeper-backend 2>nul
docker rmi talekeeper_frontend 2>nul
docker rmi talekeeper_backend 2>nul

echo [INFO] Cleaning Docker build cache...
docker builder prune -f

echo.
echo [SUCCESS] Docker cleanup complete!
echo You can now run: start-game.bat and select Docker mode
echo.
pause