@echo off
REM This batch file runs the Ultra Pong Psychosis game.

REM Ensure the Python executable is correct.
REM If 'python' doesn't work, try 'py', 'python3',
REM or the full path to your python.exe.
set PYTHON_EXECUTABLE=python

REM Get the directory where this batch file is located.
set SCRIPT_DIR=%~dp0

REM Change the current directory to the script's directory.
REM This ensures that the Python script can find its related files (config.py, sprites.py, etc.)
cd /d "%SCRIPT_DIR%"

echo Starting Ultra Pong Psychosis...
echo Folder: %SCRIPT_DIR%
echo Running: %PYTHON_EXECUTABLE% game.py
echo ============================================
echo.

REM Run the Python game script.
%PYTHON_EXECUTABLE% game.py

REM Pause the command window after the game exits to see any messages or errors.
echo.
echo ============================================
echo Game has exited. Press any key to close this window.
pause >nul
