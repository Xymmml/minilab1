@echo off
chcp 65001 >nul
echo Starting Creator Cloud Studio...

cd /d "%~dp0"

echo Starting Data Service (Port 5003)...
start "DataService" python containers\data_service\app.py

echo Starting Workflow Service (Port 5002)...
start "WorkflowService" python containers\workflow_service\app.py

echo Starting Presentation Service (Port 5001)...
start "PresentationService" python containers\presentation_service\app.py

echo.
echo All services started!
echo Open http://localhost:5001 in your browser
pause
