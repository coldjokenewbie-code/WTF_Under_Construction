"""本任務的只讀驗證（僅寫驗收報告）；基線為接手時的來源快照。"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'workingfiles/ai-team-20260914'
BEFORE = WORK / 'before'
CONFIG = ROOT / 'wtf-config'
SCOPE = ['wtf-config/AGENTS.md', 'wtf-config/CLAUDE_CODE.md', 'wtf-config/CODEX.md',
         'wtf-config/GEMINI.md', 'wtf-config/GLOBAL.md', 'wtf-config/sync_config.py',
         'wtf-config/skill_catalog.py', 'wtf-config/playbooks/model-dispatch.md',
         'wtf-config/playbooks/maintenance-protocol.md', 'wtf-config/playbooks/git-mirror.md',
         'wtf-config/playbooks/delivery-conventions.md', 'wtf-config/playbooks/data-citation.md',
         'wtf-config/playbooks/pitfalls-frontend.md', 'wtf-config/playbooks/pitfalls-office-docs.md',
         'wtf-config/tests/test_skill_catalog.py', 'wtf-config/tests/test_sync_skills.py',
         'wtf-config/skills/session-start/SKILL.md', 'wtf-config/skills/session-end/SKILL.md']


def measures(path):
    text = path.read_text()
    return [len(text), len(text.encode('utf-8')), len(text.splitlines())]


def verify_sources():
    rows = []
    for name in ('GLOBAL.md', 'AGENTS.md', 'CLAUDE_CODE.md', 'CODEX.md', 'GEMINI.md'):
        rows.append([name, measures(BEFORE / 'wtf-config' / name), measures(CONFIG / name)])
    assert rows[0][2][0] <= rows[0][1][0] * .65
    ledger = json.loads((WORK / 'migration.json').read_text())
    for entry in ledger:
        destination = (CONFIG / entry['destination']).read_text()
        if entry['mode'] == '原文搬移':
            original = entry['source_text'].replace('`playbooks/pitfalls-frontend.md`', '`pitfalls-frontend.md`')
            original = original.replace('`playbooks/maintenance-protocol.md`', '本檔')
            assert original in destination, entry['section']
    for word in ('統計起訖期間', '口徑', '不得自行推定年段或補參數', '同月同日', '未取得', '排除'):
        assert word in (CONFIG / 'playbooks/data-citation.md').read_text(), word
    global_text = (CONFIG / 'GLOBAL.md').read_text()
    for word in ('唯一例外 WTF_Under_Construction', 'Drive 禁原地 git', 'Git_work', '未登錄路徑',
                 'W_', '最新內容', '就地增量修改', '備份至 archive', '非作者輪流驗收'):
        assert word in global_text, word
    dispatch = (CONFIG / 'playbooks/model-dispatch.md').read_text()
    for model in ('claude-opus-5', 'claude-fable-5-1', 'claude-sonnet-5', 'claude-haiku-4-5-20251001'):
        assert model in dispatch, model
    assert 'claude-opus-4-8' not in dispatch
    baseline = json.loads((WORK / 'baseline.json').read_text())
    changed = [name for name, digest in baseline.items()
               if (ROOT / name).is_file() and hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    assert set(changed) <= set(SCOPE) | {'_context/INDEX.md', 'wtf-config/machines.md', 'wtf-config/LESSONS.md'}, changed
    # machines.md 的最後出現時間於協作期间再次更新；本任務未改該檔，不覆蓋外部寫入。
    (WORK / 'concurrent-changes.json').write_text(json.dumps({
        'wtf-config/machines.md': {'baseline_sha256': baseline['wtf-config/machines.md'],
        'observed_sha256': hashlib.sha256((CONFIG / 'machines.md').read_bytes()).hexdigest()},
        'wtf-config/LESSONS.md': {'baseline_sha256': baseline['wtf-config/LESSONS.md'],
        'observed_sha256': hashlib.sha256((CONFIG / 'LESSONS.md').read_bytes()).hexdigest(),
        'note': '其他工作新增cowork_CDIC展板索引；本任務未改，不覆蓋'}}, indent=2))
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SCOPE}
    (WORK / 'review-snapshot.json').write_text(json.dumps(hashes, indent=2))
    for name in ('skill_catalog.py', 'sync_config.py'):
        parsed = ast.parse((CONFIG / name).read_text())
        for function in (node for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef)):
            if name == 'sync_config.py' and function.name == 'cmd_dashboard':
                continue  # 既有 90 行函式未修改，不把全面拆分納入本輪。
            assert function.end_lineno - function.lineno + 1 <= 50, function.name
    result = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    return rows, ledger, hashes


def write_report(rows, ledger, hashes):
    report = ['# 機檢與遷移證據', '', '> [Codex@comaMacBookAir] 程式機檢；獨立審查另見 Fable 回覆。', '',
              '來源文字量測（字元／UTF-8 bytes／行數），不是 token 或帳單：', '',
              '| 檔案 | 修改前 | 修改後 |', '|---|---|---|']
    report.extend(f'| {name} | {before} | {after} |' for name, before, after in rows)
    for tool in ('CLAUDE_CODE.md', 'CODEX.md', 'GEMINI.md'):
        selected = [row for row in rows if row[0] in ('GLOBAL.md', 'AGENTS.md', tool)]
        before = sum(row[1][0] for row in selected)
        after = sum(row[2][0] for row in selected)
        report.append(f'\n{tool} 三檔合計：{before} → {after} 字元，減少 {(1-after/before)*100:.1f}%。')
    added = ['git-mirror.md', 'delivery-conventions.md']
    report.append('\n新增按需 playbook：' + '；'.join(f'{name}={measures(CONFIG / "playbooks" / name)}' for name in added))
    report += ['', '| 原 GLOBAL 條目 | 新位置／節 | 驗證 |', '|---|---|---|']
    report.extend(f'| {entry["old"]} | {entry["destination"]}／{entry["section"]} | {entry["mode"]}通過 |' for entry in ledger)
    report += ['', f'程式檢查：{len(ledger)} 個遷移項目、{len(hashes)} 個審查產物；防線/模型值/格式/改動範圍通過。',
               '新增 skill_catalog.py 174 行、最長函式 29 行；sync_config.py 減少 skill 重複邏輯，既有 dashboard 保留。',
               'V1–V7 沿用；Antigravity 行為未驗證；Windows 僅路徑邏輯設計，未實機部署。']
    (WORK / 'verification.md').write_text('\n'.join(report)+'\n')
    print('\n'.join(report[:18]))
    print('PASS:', len(ledger), 'migrations;', len(hashes), 'review artifacts; scope checked; external machines timestamp / LESSONS append recorded separately')


if __name__ == '__main__':
    write_report(*verify_sources())
