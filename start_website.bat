@echo off
setlocal
cd /d "%~dp0"

echo Dang khoi dong Backend va Frontend cho Website...

:: Khoi dong Backend trong cua so rieng
start "Website Backend (Django / Waitress: 8002 & 8000)" cmd /k "cd /d %~dp0backend && runserver.bat"

:: Khoi dong Frontend trong cua so rieng
start "Website Frontend (Port 4173)" cmd /k "cd /d %~dp0.. && python -m http.server 4173 --directory website"

:: Doi 2 giay de server khoi tao xong roi mo trinh duyet
ping 127.0.0.1 -n 3 >nul
start http://127.0.0.1:4173/

echo ============================================================
echo   Website Frontend: http://127.0.0.1:4173/
echo   Backend API:      http://127.0.0.1:8002/api/v1/health/
echo   Django Admin:     http://127.0.0.1:8002/admin/
echo ============================================================
