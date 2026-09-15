"""忠實保存 agy 文字回覆的三份成品，並記錄作者雜湊。"""
from pathlib import Path
import hashlib
import json
import re
import sys

WORK = Path(__file__).resolve().parent
OUT = WORK.parent / 'outputs' / '簡報_2026-09-14_制度優化'
name = sys.argv[1]
if name not in {'implement', 'fix1', 'fix2'}:
    raise SystemExit('Unknown task')
raw = (WORK / f'{name}.response.txt').read_text()
parts = re.findall(
    r'^===FILE:([^\n]+)===\n(.*?)^===END_FILE===', raw, re.M | re.S)
if [filename for filename, _ in parts] != ['index.html', 'styles.css', 'app.js']:
    raise SystemExit('Unexpected output format; no files written')
OUT.mkdir(parents=True, exist_ok=True)
report = {}
for filename, code in parts:
    (OUT / filename).write_text(code)
    report[filename] = {
        'lines': len(code.splitlines()),
        'sha256': hashlib.sha256(code.encode()).hexdigest()}
(WORK / f'authorship-{name}.json').write_text(
    json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
