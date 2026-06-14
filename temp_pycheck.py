import sys, pkgutil, importlib.util
with open('temp_pycheck.out', 'w') as f:
    f.write('executable=' + sys.executable + '\n')
    f.write('version=' + sys.version.replace('\n',' ') + '\n')
    f.write('fastapi=' + str(importlib.util.find_spec('fastapi') is not None) + '\n')
    f.write('uvicorn=' + str(importlib.util.find_spec('uvicorn') is not None) + '\n')
    f.write('packages=' + ','.join([m.name for m in pkgutil.iter_modules()][:50]) + '\n')
