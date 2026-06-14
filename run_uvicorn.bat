@echo off
cd /d "%~dp0"
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" -m uvicorn api.bridge:app --host 0.0.0.0 --port 8000
