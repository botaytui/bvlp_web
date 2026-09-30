@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Chua co virtual environment. Xem README.md de cai dependencies.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" manage.py migrate --noinput
if errorlevel 1 (
  echo Khong the ket noi hoac migrate PostgreSQL.
  pause
  exit /b 1
)

.venv\Scripts\python.exe manage.py collectstatic --noinput
if errorlevel 1 (
  echo Khong the thu thap static files cho Django Admin.
  pause
  exit /b 1
)

echo Backend dang chay tai http://127.0.0.1:8002 va http://127.0.0.1:8000
".venv\Scripts\waitress-serve.exe" --listen=127.0.0.1:8002 --listen=127.0.0.1:8000 hospital_backend.wsgi:application
