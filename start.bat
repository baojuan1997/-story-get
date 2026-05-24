@echo off
chcp 65001 >nul

echo ========================================
echo   播客助手 - 启动中
echo ========================================
echo.

echo [1/4] 检查 Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo.
echo [2/4] 安装后端依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] 检查前端依赖...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo    正在安装前端依赖...
    call npm install --legacy-peer-deps
)
cd /d "%~dp0"

echo.
echo [4/4] 启动服务...

start "Backend" cmd /k "title Podcast Backend && cd /d "%~dp0" && python -m backend.main"
timeout /t 2 /nobreak >nul
start "Frontend" cmd /k "title Podcast Frontend && cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo   前端界面: http://localhost:5173
echo   API 文档:  http://localhost:8765/docs
echo ========================================
echo.
echo 服务已启动！关闭本窗口不会停止服务。
echo 停止服务请关闭 "Backend" 和 "Frontend" 两个窗口。
echo.
pause
