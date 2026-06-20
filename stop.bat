@echo off
title AI Interview Platform - Stopping
color 0C

echo ============================================
echo    Stopping AI Interview Platform...
echo ============================================
echo.

:: Kill Python (backend)
taskkill /F /IM python.exe 2>NUL
echo [1/2] Backend stopped.

:: Kill Node (frontend)
taskkill /F /IM node.exe 2>NUL
echo [2/2] Frontend stopped.

echo.
echo All services stopped.
timeout /t 3 /nobreak >NUL
