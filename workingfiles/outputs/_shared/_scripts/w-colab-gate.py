#!/usr/bin/env python3
"""PreToolUse gate：共編檔（檔名以 W_ 開頭）機器把關。

退回兩種寫入：
  1. Write 工具覆蓋既有共編檔（整檔覆蓋）。
  2. 其他寫入（Edit／MultiEdit／NotebookEdit／Bash 寫入）時，同層 archive/ 沒有涵蓋現行版本的備份。

「備份涵蓋現行版本」成立條件（任一）：
  (a) 同層 archive/ 內有同副檔名（不分大小寫）、檔名（NFC）含完整主檔名（其後接分隔符或副檔名點）的檔案 B，
      且 B.mtime >= T.mtime - 2。
  (b) state 檔記錄本 hook 上次放行寫入 T 的時間 allowed_at，且 T.mtime <= allowed_at + 180
      （T 最後一次變動是 AI 剛才已把關的寫入，連續修改不必每刀重備份）。

豁免：路徑中任一層資料夾名為 archive 或以 _待刪_ 開頭；basename 以 ~$ 開頭；不存在的 W_ 檔（新建）。

已知限制：只看命令字面出現的路徑；變數、glob 展開、腳本內部組出來的路徑看不到；
腳本內部的整檔重建也無從得知，這些仍靠 W_colab 守則自律。Bash 以引號感知切段，
但不解析 here-doc、子殼層、命令替換。(b) 的 180 秒窗內若使用者同時編輯，無法察覺。

通則：空 stdin／非 JSON 放行；任何未預期例外記 log 後放行；關閉開關檔 w-colab-gate.off 存在即整支放行。
狀態目錄預設為 home 下 .claude 的 wtf-session-state，可用環境變數 W_COLAB_GATE_STATE_DIR 覆寫。
規則出處：GLOBAL.md「共編檔鐵律」與 /W_colab skill。"""
import datetime
import json
import os
import re
import shlex
import sys
import time
import unicodedata

READ_ONLY = {'ls', 'lsof', 'stat', 'md5', 'md5sum', 'shasum', 'file', 'du', 'head', 'tail', 'wc',
             'unzip', 'zipinfo', 'cat', 'open', 'diff', 'cmp', 'grep', 'rg', 'find', 'mdfind',
             'echo', 'printf', 'less', 'more', 'xxd', 'strings', 'jq', 'awk', 'cut', 'sort', 'uniq',
             'tr', 'basename', 'dirname', 'realpath', 'test', '[',
             'mdls', 'qlmanage', 'pdftotext', 'pdfinfo', 'nl', 'od', 'hexdump', 'sha256sum', 'cksum',
             'comm', 'column'}
GIT_READ = {'add', 'commit', 'diff', 'log', 'status', 'show', 'blame', 'ls-files'}
COPY_CMDS = {'cp', 'rsync', 'ditto'}
SEPS = set('_-. ()（）[]')


def state_dir():
    return os.environ.get('W_COLAB_GATE_STATE_DIR') or os.path.join(
        os.path.expanduser('~'), '.claude', 'wtf-session-state')


def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def _log(line):
    try:
        d = state_dir()
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'w-colab-gate.log'), 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def nfc(s):
    return unicodedata.normalize('NFC', s)


# ---------- 路徑判定 ----------
def exempt(path):
    parts = path.split(os.sep)
    for part in parts[:-1]:
        if part == 'archive' or part.startswith('_待刪_'):
            return True
    return os.path.basename(path).startswith('~$')


def is_target(path):
    b = os.path.basename(path)
    if not b.startswith('W_') or not os.path.splitext(b)[1]:
        return False
    if exempt(path):
        return False
    return os.path.isfile(path)


def resolve(cand, bases):
    """候選字串 → 可能的絕對路徑清單。"""
    cand = os.path.expanduser(cand.strip())
    if not cand:
        return []
    if os.path.isabs(cand):
        return [os.path.normpath(cand)]
    return [os.path.normpath(os.path.join(b, cand)) for b in bases]


def targets_from(cands, bases):
    out = []
    for c in cands:
        for p in resolve(c, bases):
            if is_target(p) and p not in out:
                out.append(p)
    return out


# ---------- Bash 解析 ----------
def split_segments(cmd):
    """依 && || ; | 換行 切段，引號內不切。"""
    segs, buf, q, i, n = [], [], None, 0, len(cmd)
    while i < n:
        ch = cmd[i]
        if q:
            buf.append(ch)
            if ch == '\\' and q == '"' and i + 1 < n:
                buf.append(cmd[i + 1])
                i += 1
            elif ch == q:
                q = None
        elif ch in '"\'':
            q = ch
            buf.append(ch)
        elif ch == '\\' and i + 1 < n:
            buf.append(ch)
            buf.append(cmd[i + 1])
            i += 1
        elif ch in ';\n' or ch == '|' or (ch == '&' and i + 1 < n and cmd[i + 1] == '&'):
            segs.append(''.join(buf))
            buf = []
            if (ch == '|' and i + 1 < n and cmd[i + 1] == '|') or ch == '&':
                i += 1
        else:
            buf.append(ch)
        i += 1
    segs.append(''.join(buf))
    return [s.strip() for s in segs if s.strip()]


def tokens_of(seg):
    try:
        return shlex.split(seg)
    except ValueError:
        return seg.split()


def literal_cands(seg, toks):
    """段內所有可能的路徑字面：雙引號、單引號、無引號 token、shlex token。"""
    c = []
    c += re.findall(r'"([^"\n]*)"', seg)
    c += re.findall(r"'([^'\n]*)'", seg)
    bare = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', ' ', seg)
    c += [x for x in re.split(r'[\s=,()<>]+', bare) if x]
    for t in toks:
        c.append(t)
        if '=' in t:
            c.append(t.split('=', 1)[1])
    return c


REDIR = re.compile(r'^\d*>>?(.*)$')


def redirect_targets(toks):
    out = []
    for i, t in enumerate(toks):
        m = REDIR.match(t)
        if not m:
            continue
        rest = m.group(1)
        if rest.startswith('&'):
            continue
        if rest:
            out.append(rest)
        elif i + 1 < len(toks):
            out.append(toks[i + 1])
    return out


def bash_writes(cmd, cwd):
    segs = [x for x in (s.lstrip('({ \t').rstrip(' \t)}') for s in split_segments(cmd)) if x]
    bases = [cwd]
    if segs:
        t0 = tokens_of(segs[0])
        if len(t0) >= 2 and t0[0] == 'cd':
            d = os.path.expanduser(t0[1])
            d = d if os.path.isabs(d) else os.path.join(cwd, d)
            bases.append(os.path.normpath(d))
    written = []

    def add(lst):
        for p in lst:
            if p not in written:
                written.append(p)

    for seg in segs:
        toks = tokens_of(seg)
        i = 0
        while i < len(toks) and re.match(r'^[A-Za-z_]\w*=', toks[i]):
            i += 1
        toks_h = toks[i:]
        if not toks_h:
            continue
        head = os.path.basename(toks_h[0])
        # 輸出重導優先
        rt = redirect_targets(toks_h)
        if rt:
            add(targets_from(rt, bases))
        if head in READ_ONLY:
            continue
        if head == 'sed' and not any(t.startswith('-i') or t == '--in-place' or t.startswith('--in-place=')
                                      for t in toks_h[1:]):
            continue
        if head == 'git':
            sub = next((t for t in toks_h[1:] if not t.startswith('-')), '')
            if sub in GIT_READ:
                continue
        if head in COPY_CMDS and len(toks_h) >= 3:
            dest = toks_h[-1]
            srcs = [t for t in toks_h[1:-1] if not t.startswith('-')]
            dcands = []
            for dp in resolve(dest, bases):
                if os.path.isdir(dp):
                    dcands += [os.path.join(dp, os.path.basename(s.rstrip('/'))) for s in srcs]
                else:
                    dcands.append(dp)
            add(targets_from(dcands, ['/']))
            continue
        add(targets_from(literal_cands(seg, toks_h), bases))
    return written


# ---------- state ----------
def load_state():
    try:
        with open(os.path.join(state_dir(), 'w-colab-gate-state.json'), encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def save_state(st):
    try:
        d = state_dir()
        os.makedirs(d, exist_ok=True)
        tmp = os.path.join(d, 'w-colab-gate-state.json.tmp%d' % os.getpid())
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(st, f, ensure_ascii=False)
        os.replace(tmp, os.path.join(d, 'w-colab-gate-state.json'))
    except Exception:
        pass


def backup_covers(t, st):
    try:
        tm = os.path.getmtime(t)
    except OSError:
        return True
    d = os.path.dirname(t)
    stem = nfc(os.path.splitext(os.path.basename(t))[0])
    ext = os.path.splitext(t)[1].lower()
    ad = os.path.join(d, 'archive')
    try:
        for name in os.listdir(ad):
            if os.path.splitext(name)[1].lower() != ext:
                continue
            nn = nfc(name)
            hit = False
            pos = nn.find(stem)
            while pos >= 0:
                end = pos + len(stem)
                if end >= len(nn) or nn[end] in SEPS:
                    hit = True
                    break
                pos = nn.find(stem, pos + 1)
            if hit:
                bp = os.path.join(ad, name)
                if os.path.isfile(bp) and os.path.getmtime(bp) >= tm - 2:
                    return True
    except OSError:
        pass
    at = st.get(t)
    if isinstance(at, (int, float)) and tm <= at + 180:
        return True
    return False


def disp(t, cwd):
    """T 在 cwd 之內用相對路徑（避免 Drive 絕對路徑含帳號 email），否則維持絕對路徑。"""
    try:
        rel = os.path.relpath(t, os.path.normpath(cwd))
    except ValueError:
        return t
    if rel == '..' or rel.startswith('..' + os.sep) or os.path.isabs(rel):
        return t
    return rel


def backup_cmd(t, cwd):
    p = disp(t, cwd)
    d = os.path.dirname(p)
    stem, ext = os.path.splitext(os.path.basename(p))
    ts = time.strftime('%y%m%d-%H%M')
    arch = os.path.join(d, 'archive') if d else 'archive'
    return 'mkdir -p "%s" && cp -p "%s" "%s/%s_%s%s"' % (arch, p, arch, stem, ts, ext)


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        data = json.loads(raw)
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0
    ti = data.get('tool_input') or {}
    tool = data.get('tool_name', '')
    cwd = data.get('cwd') or os.getcwd()
    if tool in ('Write', 'Edit', 'MultiEdit'):
        written = targets_from([ti.get('file_path') or ''], [cwd])
    elif tool == 'NotebookEdit':
        written = targets_from([ti.get('notebook_path') or ''], [cwd])
    elif tool == 'Bash':
        written = bash_writes(ti.get('command') or '', cwd)
    else:
        return 0
    if not written:
        return 0
    st = load_state()
    bad = []
    for t in written:
        if tool == 'Write':
            bad.append((t, 'Write 整檔覆蓋既有共編檔'))
        elif not backup_covers(t, st):
            bad.append((t, '同層 archive/ 沒有涵蓋現行版本的備份（檔案在上次備份後被改過，可能是使用者編輯）'))
    if not bad:
        t_now = time.time()
        for t in written:
            st[t] = t_now
        save_state(st)
        return 0
    lines = ['[w-colab-gate] 拒絕：下列共編檔（W_ 開頭）不得這樣寫入。']
    for t, why in bad:
        lines.append('  - %s：%s' % (disp(t, cwd), why))
    lines.append('做法：')
    lines.append('  1. 先重新讀取該檔最新內容，不得沿用對話裡的舊版。')
    lines.append('  2. 先備份（逐檔照下列指令執行）：')
    for t, _ in bad:
        lines.append('  備份指令：' + backup_cmd(t, cwd))
    if tool != 'Write':
        lines.append('     若這條指令只是讀取：照上面備份一次即可，之後檔案未再變動前都會放行。')
    lines.append('  3. 之後只做就地增量修改（Edit 或局部腳本），禁止產生器／整檔重建；Write 不可用於既有共編檔。')
    lines.append('規則出處：GLOBAL.md「共編檔鐵律」與 /W_colab skill。')
    sys.stderr.write('\n'.join(lines) + '\n')
    return 2


if __name__ == '__main__':
    try:
        if os.path.exists(os.path.join(state_dir(), 'w-colab-gate.off')):
            sys.exit(0)
        rc = main()
    except SystemExit:
        raise
    except Exception as e:  # noqa
        _log('%s\tERROR-passthrough\t%r' % (now_iso(), e))
        sys.exit(0)
    if rc == 2:
        _log('%s\tBLOCK\t%s' % (now_iso(), os.getcwd()))
    sys.exit(rc)
