"""已驗收 SSOT 的本機部署與第二次同步內容比對；不執行 git 或遠端操作。"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'workingfiles/ai-team-20260914'
sys.path.insert(0, str(ROOT / 'wtf-config'))
SPEC = importlib.util.spec_from_file_location('sync_config', ROOT / 'wtf-config/sync_config.py')
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


def snapshot():
    paths = {directory / 'AGENTS.md' for directory in SYNC.registry_dirs()}
    paths.add(SYNC.CLAUDE_DIR / 'CLAUDE.md')
    paths.update(tool['home'] / tool['instr_dst'] for tool in SYNC.OTHER_TOOLS if tool['home'].is_dir())
    extras = {}
    for target in SYNC._skill_targets():
        paths.add(target['index_path'])
        known = set()
        for skill in SYNC.read_skills(target['source']):
            known.add(skill['directory'].name)
            paths.update(target['destination'] / skill['directory'].name / item.relative_to(skill['directory'])
                         for item in skill['directory'].rglob('*') if item.is_file())
        extras[str(target['destination'])] = sorted(path.name for path in target['destination'].iterdir()
                                                    if path.name not in known)
    hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}
    return {'sha256': hashes, 'extra_entries': extras}


def run_command(action, name):
    result = subprocess.run([sys.executable, str(ROOT / 'wtf-config/sync_config.py'), action],
                            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (WORK / name).write_text(result.stdout)
    if result.returncode:
        print(result.stdout)
        raise SystemExit(result.returncode)


def main():
    expected = json.loads((WORK / 'review-snapshot.json').read_text())
    for name, digest in expected.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    before = snapshot()
    run_command('sync', 'deploy-first.log')
    first = snapshot()
    run_command('sync', 'deploy-second.log')
    second = snapshot()
    run_command('check', 'deploy-check.log')
    assert first == second, '第二次部署內容不同，需核對並行寫入'
    assert before['extra_entries'] == second['extra_entries'], '額外技能清單有變，需核對'
    (WORK / 'deployment-snapshot.json').write_text(json.dumps(second, ensure_ascii=False, indent=2))
    count = len(second['sha256'])
    summary = f'PASS: sync x2 + check; {count} deployed files identical after second sync; extra skill entries preserved.\n'
    (WORK / 'deployment-result.txt').write_text(summary)
    print(summary)


if __name__ == '__main__':
    main()
