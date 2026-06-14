import subprocess, sys
cmd = [sys.executable, '-m', 'pip', 'list']
proc = subprocess.run(cmd, capture_output=True, text=True)
with open('temp_pip_list.txt', 'w', encoding='utf-8') as f:
    f.write('command=' + ' '.join(cmd) + '\n')
    f.write('returncode=' + str(proc.returncode) + '\n')
    f.write('stdout:\n' + proc.stdout + '\n')
    f.write('stderr:\n' + proc.stderr + '\n')
