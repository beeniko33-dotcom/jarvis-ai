import uvicorn, sys
print('uvicorn_version:', getattr(uvicorn, '__version__', 'n/a'))
print('python_executable:', sys.executable)
