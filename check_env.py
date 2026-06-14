import socket
import importlib.util
import sys

def check_module(name):
    spec = importlib.util.find_spec(name)
    print(f"{name}:", "FOUND" if spec else "MISSING")

print('python:', sys.executable)
print('version:', sys.version.replace('\n', ' '))
for mod in ['fastapi', 'uvicorn', 'pydantic', 'dotenv', 'chromadb', 'ollama']:
    check_module(mod)

sock = socket.socket()
try:
    sock.settimeout(2)
    sock.connect(('127.0.0.1', 8000))
    print('port 8000: OPEN')
except Exception as e:
    print('port 8000: CLOSED', repr(e))
finally:
    sock.close()
