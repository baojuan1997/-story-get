@echo off
chcp 65001 >nul 2>&1

cd /d "%~dp0"

echo Starting backend...
start "Backend [8765]" cmd /k "python -m backend.main"
