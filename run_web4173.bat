@echo off
setlocal EnableExtensions EnableDelayedExpansion
title BVLP Website Manager

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"
set "WAITRESS_EXE=%BACKEND_DIR%\.venv\Scripts\waitress-serve.exe"
set "RUNTIME_DIR=%TEMP%\bvlp_web4173"
set "FRONTEND_PID=%RUNTIME_DIR%\frontend.pid"
set "BACKEND_PID=%RUNTIME_DIR%\backend.pid"
set "FRONTEND_OUT=%RUNTIME_DIR%\frontend.out.log"
set "FRONTEND_ERR=%RUNTIME_DIR%\frontend.err.log"
set "BACKEND_OUT=%RUNTIME_DIR%\backend.out.log"
set "BACKEND_ERR=%RUNTIME_DIR%\backend.err.log"

cd /d "%PROJECT_DIR%"

set "ACTION=%~1"
if not defined ACTION set "ACTION=start"

if /I "%ACTION%"=="start" goto :start_services
if /I "%ACTION%"=="stop" goto :stop_services
if /I "%ACTION%"=="restart" goto :restart_services
if /I "%ACTION%"=="status" goto :status_services
if /I "%ACTION%"=="logs" goto :show_logs
if /I "%ACTION%"=="open" goto :open_browser
if /I "%ACTION%"=="help" goto :usage
if /I "%ACTION%"=="--help" goto :usage
goto :usage_error

:start_services
call :ensure_setup
if errorlevel 1 exit /b 1

if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%BACKEND_DIR%\data" mkdir "%BACKEND_DIR%\data"

echo [SETUP] Cap nhat database va static files...
pushd "%BACKEND_DIR%"
"%VENV_PYTHON%" manage.py migrate --noinput
if errorlevel 1 (
  popd
  echo [LOI] Khong the migrate database.
  exit /b 1
)
"%VENV_PYTHON%" manage.py collectstatic --noinput --verbosity 0
if errorlevel 1 (
  popd
  echo [LOI] Khong the collect static files.
  exit /b 1
)
popd

call :port_is_listening 8002
if not errorlevel 1 (
  echo [INFO] Backend da dang lang nghe tren cong 8002.
) else (
  echo [START] Backend Django chay ngam tren 127.0.0.1:8002...
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=Start-Process -FilePath $env:WAITRESS_EXE -ArgumentList @('--listen=127.0.0.1:8002','hospital_backend.wsgi:application') -WorkingDirectory $env:BACKEND_DIR -WindowStyle Hidden -RedirectStandardOutput $env:BACKEND_OUT -RedirectStandardError $env:BACKEND_ERR -PassThru; Set-Content -LiteralPath $env:BACKEND_PID -Value $p.Id -Encoding ascii"
  if errorlevel 1 (
    echo [LOI] Khong the khoi dong backend.
    exit /b 1
  )
)

call :port_is_listening 4173
if not errorlevel 1 (
  echo [INFO] Frontend da dang lang nghe tren cong 4173.
) else (
  echo [START] Frontend chay ngam tren 127.0.0.1:4173...
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=Start-Process -FilePath $env:VENV_PYTHON -ArgumentList @('-m','http.server','4173','--bind','127.0.0.1') -WorkingDirectory $env:PROJECT_DIR -WindowStyle Hidden -RedirectStandardOutput $env:FRONTEND_OUT -RedirectStandardError $env:FRONTEND_ERR -PassThru; Set-Content -LiteralPath $env:FRONTEND_PID -Value $p.Id -Encoding ascii"
  if errorlevel 1 (
    echo [LOI] Khong the khoi dong frontend.
    call :stop_by_pid_file "%BACKEND_PID%"
    exit /b 1
  )
)

ping 127.0.0.1 -n 4 >nul
call :print_status
echo.
echo [OK] Hai dich vu dang chay ngam, khong mo them cua so CMD.
echo [INFO] Quan ly trong ConEmu bang: start, stop, restart, status, logs, open
exit /b 0

:stop_services
echo [STOP] Dang dung frontend va backend...
call :stop_by_pid_file "%FRONTEND_PID%"
call :stop_by_pid_file "%BACKEND_PID%"
call :stop_by_port 4173
call :stop_by_port 8002
echo [OK] Da dung cac dich vu tren cong 4173 va 8002.
exit /b 0

:restart_services
call :stop_services
goto :start_services

:status_services
call :print_status
exit /b 0

:show_logs
if not exist "%RUNTIME_DIR%" (
  echo [INFO] Chua co log. Hay chay "%~nx0 start" truoc.
  exit /b 0
)
echo ============================================================
echo FRONTEND STDOUT: %FRONTEND_OUT%
if exist "%FRONTEND_OUT%" powershell.exe -NoProfile -Command "Get-Content -LiteralPath $env:FRONTEND_OUT -Tail 30"
echo.
echo FRONTEND STDERR: %FRONTEND_ERR%
if exist "%FRONTEND_ERR%" powershell.exe -NoProfile -Command "Get-Content -LiteralPath $env:FRONTEND_ERR -Tail 30"
echo.
echo BACKEND STDOUT: %BACKEND_OUT%
if exist "%BACKEND_OUT%" powershell.exe -NoProfile -Command "Get-Content -LiteralPath $env:BACKEND_OUT -Tail 30"
echo.
echo BACKEND STDERR: %BACKEND_ERR%
if exist "%BACKEND_ERR%" powershell.exe -NoProfile -Command "Get-Content -LiteralPath $env:BACKEND_ERR -Tail 30"
echo ============================================================
exit /b 0

:open_browser
start "" "http://127.0.0.1:4173/"
exit /b 0

:ensure_setup
if not exist "%VENV_PYTHON%" (
  echo [SETUP] Dang tao Python virtual environment...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv "%BACKEND_DIR%\.venv"
  ) else (
    python -m venv "%BACKEND_DIR%\.venv"
  )
  if errorlevel 1 (
    echo [LOI] Khong the tao virtual environment.
    exit /b 1
  )
)

if not exist "%WAITRESS_EXE%" (
  echo [SETUP] Dang cai dependencies cho backend...
  "%VENV_PYTHON%" -m pip install -r "%BACKEND_DIR%\requirements.txt"
  if errorlevel 1 (
    echo [LOI] Khong the cai dependencies.
    exit /b 1
  )
)
exit /b 0

:port_is_listening
netstat -ano -p tcp | findstr /R /C:"127.0.0.1:%~1 .*LISTENING" >nul
exit /b %errorlevel%

:stop_by_pid_file
if not exist "%~1" exit /b 0
set "SERVICE_PID="
set /p SERVICE_PID=<"%~1"
if defined SERVICE_PID taskkill /PID !SERVICE_PID! /T /F >nul 2>nul
del /Q "%~1" >nul 2>nul
exit /b 0

:stop_by_port
set "TARGET_PORT=%~1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ids=@(); netstat -ano -p tcp | ForEach-Object { if ($_ -match ('^\s*TCP\s+\S+:' + $env:TARGET_PORT + '\s+\S+\s+LISTENING\s+(\d+)\s*$')) { $ids += [int]$Matches[1] } }; $ids | Sort-Object -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
exit /b 0

:print_status
echo ============================================================
call :port_is_listening 4173
if errorlevel 1 (echo   Frontend 4173: OFFLINE) else (echo   Frontend 4173: ONLINE  - http://127.0.0.1:4173/)
call :port_is_listening 8002
if errorlevel 1 (echo   Backend  8002: OFFLINE) else (echo   Backend  8002: ONLINE  - http://127.0.0.1:8002/api/v1/health/)
echo   Logs: %RUNTIME_DIR%
echo ============================================================
exit /b 0

:usage
echo.
echo Dung trong ConEmu:
echo   %~nx0 start    - Chay frontend/backend ngam, khong mo CMD moi
echo   %~nx0 stop     - Dung ca hai dich vu
echo   %~nx0 restart  - Khoi dong lai ca hai dich vu
echo   %~nx0 status   - Xem trang thai cong 4173 va 8002
echo   %~nx0 logs     - Xem 30 dong log gan nhat
echo   %~nx0 open     - Mo website trong trinh duyet
echo.
exit /b 0

:usage_error
echo [LOI] Lenh khong hop le: %ACTION%
call :usage
exit /b 1
