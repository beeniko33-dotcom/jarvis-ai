$ErrorActionPreference = 'Stop'
Set-Location 'C:\Users\rmden\Downloads\jarvis-ai-1.0.0'
$py = 'C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe'
"Starting install at $(Get-Date)" | Out-File -FilePath pip_install_log.txt -Encoding utf8
& $py -m pip install --upgrade pip 2>&1 | Out-File -FilePath pip_install_log.txt -Append -Encoding utf8
& $py -m pip install -r requirements.txt 2>&1 | Out-File -FilePath pip_install_log.txt -Append -Encoding utf8
& $py -m pip list 2>&1 | Out-File -FilePath pip_list_after.txt -Encoding utf8
& $py -m pip show fastapi uvicorn python-dotenv pydantic 2>&1 | Out-File -FilePath pip_show.txt -Encoding utf8
"Done at $(Get-Date)" | Out-File -FilePath pip_install_log.txt -Append -Encoding utf8
