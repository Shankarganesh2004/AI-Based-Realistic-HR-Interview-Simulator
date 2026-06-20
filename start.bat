@echo off
title AI Interview Platform - Launcher
color 0A

echo ============================================
echo    AI Interview Platform - Starting...
echo ============================================
echo.

:: Start Backend
echo [1/2] Starting Backend (FastAPI on port 8000)...
start "Backend" cmd /k "cd /d c:\Users\Public\ai-interview-platform\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

:: Wait for backend to initialize
timeout /t 3 /nobreak >NUL

:: Start Frontend
echo [2/2] Starting Frontend (Vite on port 5173)...
start "Frontend" cmd /k "cd /d c:\Users\Public\ai-interview-platform\frontend && npm run dev"

echo.
echo ============================================
echo    All services started!
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo    Network:  http://10.67.51.139:5173
echo ============================================
echo.
echo Close this window anytime. Services run independently.
pause
