@echo off
title WEBSITE 4173
setlocal

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"
set "WAITRESS_EXE=%BACKEND_DIR%\.venv\Scripts\waitress-serve.exe"

cd /d "%PROJECT_DIR%"

if /I "%~1"=="backend" goto :run_backend
if /I "%~1"=="frontend" goto :run_frontend

if not exist "%VENV_PYTHON%" (
  echo [SETUP] Dang tao Python virtual environment...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv "%BACKEND_DIR%\.venv"
  ) else (
    python -m venv "%BACKEND_DIR%\.venv"
  )
  if errorlevel 1 goto :setup_error
)

if not exist "%WAITRESS_EXE%" (
  echo [SETUP] Dang cai dependencies cho backend...
  "%VENV_PYTHON%" -m pip install -r "%BACKEND_DIR%\requirements.txt"
  if errorlevel 1 goto :setup_error
)

echo [START] Backend Django: http://127.0.0.1:8002/
start "BVLP Backend (8002)" /D "%BACKEND_DIR%" cmd /k call "%~f0" backend

echo [START] Frontend: http://127.0.0.1:4173/
start "BVLP Frontend (4173)" /D "%PROJECT_DIR%" cmd /k call "%~f0" frontend

ping 127.0.0.1 -n 4 >nul
start "" "http://127.0.0.1:4173/"

echo.
echo ============================================================
echo   Frontend:      http://127.0.0.1:4173/
echo   Backend API:   http://127.0.0.1:8002/api/v1/health/
echo   Django Admin:  http://127.0.0.1:8002/admin/
echo ============================================================
exit /b 0

:run_backend
cd /d "%BACKEND_DIR%"
if not exist "%BACKEND_DIR%\data" mkdir "%BACKEND_DIR%\data"
echo [BACKEND] Dang cap nhat database...
"%VENV_PYTHON%" manage.py migrate --noinput
if errorlevel 1 goto :runtime_error
"%VENV_PYTHON%" manage.py collectstatic --noinput
if errorlevel 1 goto :runtime_error
echo [BACKEND] Dang lang nghe tai http://127.0.0.1:8002/
"%WAITRESS_EXE%" --listen=127.0.0.1:8002 hospital_backend.wsgi:application
goto :eof

:run_frontend
cd /d "%PROJECT_DIR%"
echo [FRONTEND] Dang lang nghe tai http://127.0.0.1:4173/
"%VENV_PYTHON%" -m http.server 4173 --bind 127.0.0.1
goto :eof

:setup_error
echo.
echo [LOI] Khong the khoi tao moi truong Python cho backend.
pause
exit /b 1

:runtime_error
echo.
echo [LOI] Khong the khoi dong dich vu.
pause
exit /b 1
