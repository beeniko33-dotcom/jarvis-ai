import pkgutil
import subprocess
import sys
from pathlib import Path
p = Path('pip_status.out')
with p.open('w', encoding='utf-8') as f:
    f.write('executable=' + sys.executable + '\n')
    f.write('version=' + sys.version.replace('\n', ' ') + '\n')
    f.write('\nINSTALLED PACKAGES:\n')
    proc = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
    f.write(proc.stdout + '\n')
    f.write('pip_list_rc=' + str(proc.returncode) + '\n')
    for pkg in ['fastapi', 'uvicorn', 'kivy', 'crewai', 'chromadb', 'crewai-tools', 'websockets', 'ollama']:
        proc = subprocess.run([sys.executable, '-m', 'pip', 'show', pkg], capture_output=True, text=True)
        f.write(f'\nSHOW {pkg}: rc={proc.returncode}\n')
        f.write(proc.stdout + '\n')
    try:
        import fastapi
        f.write('fastapi_import=OK\n')
    except Exception as e:
        f.write('fastapi_import=ERR ' + repr(e) + '\n')
    try:
        import uvicorn
        f.write('uvicorn_import=OK\n')
    except Exception as e:
        f.write('uvicorn_import=ERR ' + repr(e) + '\n')
    try:
        import crewai
        f.write('crewai_import=OK\n')
    except Exception as e:
        f.write('crewai_import=ERR ' + repr(e) + '\n')
    try:
        import chromadb
        f.write('chromadb_import=OK\n')
    except Exception as e:
        f.write('chromadb_import=ERR ' + repr(e) + '\n')
    try:
        import kivy
        f.write('kivy_import=OK\n')
    except Exception as e:
        f.write('kivy_import=ERR ' + repr(e) + '\n')
    try:
        import websockets
        f.write('websockets_import=OK\n')
    except Exception as e:
        f.write('websockets_import=ERR ' + repr(e) + '\n')
