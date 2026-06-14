import subprocess, sys
from pathlib import Path
log = Path('install_run.log')
with log.open('w', encoding='utf-8') as f:
    def run(cmd):
        f.write('RUN: ' + ' '.join(cmd) + '\n')
        proc = subprocess.run(cmd, capture_output=True, text=True)
        f.write('RC=' + str(proc.returncode) + '\n')
        f.write('STDOUT:\n' + (proc.stdout or '') + '\n')
        f.write('STDERR:\n' + (proc.stderr or '') + '\n')
        f.flush()
        return proc.returncode

    py = sys.executable
    run([py, '-m', 'pip', 'install', '--upgrade', 'pip'])
    run([py, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    run([py, '-m', 'pip', 'install', 'fastapi', 'uvicorn'])

print('Done. See install_run.log')
