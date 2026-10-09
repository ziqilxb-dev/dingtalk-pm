@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\setup.py %*
) else (
  python scripts\setup.py %*
)
if errorlevel 1 echo Setup failed. Python 3.9+ and access to github.com are required.
pause
