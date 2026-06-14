@echo off
cd /d "%~dp0"
echo STARTTEST > test_python_out.txt
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" --version >> test_python_out.txt 2>&1
echo PIP >> test_python_out.txt
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" -m pip --version >> test_python_out.txt 2>&1
echo STOPTEST >> test_python_out.txt
