@echo off
setlocal

set "REPO_ROOT=%~dp0.."
cd /d "%REPO_ROOT%"
set "PYTHONPATH=%REPO_ROOT%\src;%PYTHONPATH%"

echo Starting VideoEdgeAI-Task reviewer console...
echo Repo: %CD%
echo Open: http://127.0.0.1:8000/
echo.

python -m uvicorn videoedgeai_task.main:app --host 127.0.0.1 --port 8000 --reload
