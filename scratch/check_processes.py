import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
output = subprocess.check_output(
    ['wmic', 'process', 'where', "name like '%python%'", 'get', 'processid,commandline'],
    shell=True,
    text=True,
    errors='replace'
)
print(output)
