"""依 PO 指定呼叫 agy；提示與輸出固定保存於本資料夾。"""
from pathlib import Path
import subprocess
import sys

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
name = sys.argv[1]
if name not in {'implement', 'fix1', 'fix2', 'review'}:
    raise SystemExit('Unknown task')
prompt = (WORK / f'{name}.prompt.txt').read_text()
output_path = WORK / f'{name}.response.txt'
with output_path.open('w') as output:
    try:
        result = subprocess.run(
            ['agy', '--mode', 'plan', '--print', prompt,
             '--print-timeout', '4m'],
            stdin=subprocess.DEVNULL, stdout=output,
            stderr=subprocess.STDOUT, cwd=ROOT, timeout=260)
    except subprocess.TimeoutExpired:
        print('agy timed out; partial output saved.')
        raise SystemExit(124)
print(output_path.read_text())
raise SystemExit(result.returncode)
