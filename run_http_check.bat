@echo off
cd /d "%~dp0"
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" check_http.py > httpcheck.txt 2>&1
if exist httpcheck.txt type httpcheck.txt
