$ErrorActionPreference = 'Stop'
Set-Location 'C:\Users\rmden\Downloads\jarvis-ai-1.0.0'
$py = 'C:\Users\rmden\AppData\Local\Programs\Python\Python39\python.exe'
"PY CHECK" | Out-File -FilePath pytest_out.txt -Encoding utf8
if (-Not (Test-Path $py)) {
    "PY MISSING" | Out-File -FilePath pytest_out.txt -Encoding utf8
    exit 1
}
& $py --version 2>&1 | Out-File -FilePath pyver.txt -Encoding utf8
& $py -m pip --version 2>&1 | Out-File -FilePath pipver.txt -Encoding utf8
"PY OK" | Out-File -FilePath pytest_out.txt -Append -Encoding utf8
