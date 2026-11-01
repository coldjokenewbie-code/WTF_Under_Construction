#!/usr/bin/env python3
"""PreToolUse gate：工具輸入提到的 pptx/docx/xlsx 若正被 Office 開著（~$ 鎖檔或 lsof 持有），拒絕執行。
只看字面出現的路徑；純讀取命令放行；cp/mv 只看目的端。空 stdin 放行。"""
import json, os, re, shlex, subprocess, sys

EXT = r'(?:pptx|pptm|docx|docm|xlsx|xlsm)'
PAT = re.compile(r'"([^"\n]+\.' + EXT + r')"|\'([^\'\n]+\.' + EXT + r')\'|([^\s"\'`=(),]+\.' + EXT + r')\b')
READ_ONLY = {'ls', 'lsof', 'stat', 'md5', 'md5sum', 'shasum', 'file', 'du', 'head', 'wc',
             'unzip', 'zipinfo', 'cat', 'open', 'diff', 'cmp', 'grep', 'find', 'mdfind', 'echo', 'printf'}
SRC_ONLY = {'cp', 'rsync', 'ditto'}


def lock_names(name):
    return {'~$' + name, '~$' + name[1:], '~$' + name[2:]}


def is_open(path):
    d, n = os.path.split(path)
    try:
        if any(os.path.exists(os.path.join(d, ln)) for ln in lock_names(n)):
            return 'lock'
    except OSError:
        pass
    try:
        r = subprocess.run(['lsof', '-t', '--', path], capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            return 'lsof pid ' + r.stdout.split()[0]
    except Exception:
        pass
    return None


def candidates(text, cwd):
    out = []
    for m in PAT.finditer(text):
        p = next(g for g in m.groups() if g)
        p = os.path.expanduser(p)
        if not os.path.isabs(p):
            p = os.path.join(cwd, p)
        p = os.path.normpath(p)
        if os.path.basename(p).startswith('~$'):
            continue
        if os.path.isfile(p) and p not in out:
            out.append(p)
    return out


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        data = json.loads(raw)
    except Exception:
        return 0
    ti = data.get('tool_input') or {}
    tool = data.get('tool_name', '')
    cwd = data.get('cwd') or os.getcwd()
    if tool == 'Bash':
        cmd = ti.get('command', '')
        try:
            toks = shlex.split(cmd)
        except ValueError:
            toks = cmd.split()
        simple = not re.search(r'&&|\|\||[;|>]', cmd)
        head = toks[0] if toks else ''
        if simple and head in READ_ONLY:
            return 0
        if simple and head in SRC_ONLY and len(toks) >= 3:
            text = toks[-1]
        else:
            text = cmd
    else:
        text = ' '.join(str(ti.get(k, '')) for k in ('file_path', 'content', 'new_string', 'notebook_path'))
    hits = [(p, how) for p in candidates(text, cwd) for how in [is_open(p)] if how]
    if not hits:
        return 0
    lines = ['[office-lock-gate] 拒絕：下列 Office 檔正被開著，寫入會讓 PowerPoint／Word 報「內容有問題」。']
    for p, how in hits:
        lines.append(f'  - {p}（{how}）')
    lines.append('做法：改存旁邊的複本（如 檔名_AI_MMDD-HHMM.pptx）並請 PO 原視窗不存檔關掉後自行取代；或請 PO 先關檔。'
                 '純讀取請用 cp 複製到別處再讀。規則：wtf-config/playbooks/pitfalls-office-docs.md 末段。')
    sys.stderr.write('\n'.join(lines) + '\n')
    return 2


OFF_SWITCH = os.path.expanduser('~/.claude/wtf-session-state/office-lock-gate.off')
LOG = os.path.expanduser('~/.claude/wtf-session-state/office-lock-gate.log')


def _log(line):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a') as f:
            f.write(line + '\n')
    except Exception:
        pass


if __name__ == '__main__':
    # 失效即放行：關閉開關存在、或任何未預期例外，都不得擋工具。只有「確認檔案開著」這一條路才 exit 2。
    if os.path.exists(OFF_SWITCH):
        sys.exit(0)
    try:
        rc = main()
    except Exception as e:  # noqa
        _log(f'{__import__("datetime").datetime.now().isoformat(timespec="seconds")}\tERROR-passthrough\t{e!r}')
        sys.exit(0)
    if rc == 2:
        _log(f'{__import__("datetime").datetime.now().isoformat(timespec="seconds")}\tBLOCK\t{os.getcwd()}')
    sys.exit(rc)
