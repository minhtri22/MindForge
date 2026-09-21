@echo off
setlocal
cd /d "%~dp0\.."
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_m5_f16_local.ps1"
set EXITCODE=%ERRORLEVEL%
echo.
echo Exit code: %EXITCODE%
exit /b %EXITCODE%
