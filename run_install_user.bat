@echo off
cd /d "%~dp0"

echo START > pip_install_log.txt
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" --version > cmdtest.txt 2>&1
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" -m pip install --upgrade pip --user >> pip_install_log.txt 2>&1
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" -m pip install -r requirements.txt --user >> pip_install_log.txt 2>&1
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" -m pip list > pip_list_after.txt 2>&1
"C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe" -m pip show fastapi uvicorn python-dotenv pydantic > pip_show.txt 2>&1
 echo DONE >> pip_install_log.txt
