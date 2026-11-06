#!/usr/bin/env python3
"""w-colab-gate 測試：以 subprocess 餵 JSON 給 hook，逐案印 PASS/FAIL。"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, 'w-colab-gate.py')
BASE = '/private/tmp/claude-501/-Users-coma-git-mirror-WTF-Under-Construction/54d25ba7-4bca-4266-9b68-a85c840a7885/scratchpad/wcolab_test'
WORK = os.path.join(BASE, 'work')
STATE = os.path.join(BASE, 'state')
res = []


def reset():
    for d in (WORK, STATE):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)


def w(rel, text='x\n', mtime=None):
    p = os.path.join(WORK, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    if mtime:
        os.utime(p, (mtime, mtime))
    return p


def run(payload, raw=None):
    env = dict(os.environ, W_COLAB_GATE_STATE_DIR=STATE)
    inp = raw if raw is not None else json.dumps(payload, ensure_ascii=False)
    r = subprocess.run([sys.executable, HOOK], input=inp, capture_output=True, text=True, env=env)
    return r.returncode, r.stderr


def bash(cmd, cwd=None):
    return run({'tool_name': 'Bash', 'cwd': cwd or WORK, 'tool_input': {'command': cmd}})


def tool(name, path, key='file_path'):
    return run({'tool_name': name, 'cwd': WORK, 'tool_input': {key: path}})


def check(name, got, want):
    ok = got == want
    res.append(ok)
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else '  (got %s want %s)' % (got, want)))


def backup(p):
    d = os.path.dirname(p)
    os.makedirs(os.path.join(d, 'archive'), exist_ok=True)
    stem, ext = os.path.splitext(os.path.basename(p))
    shutil.copy2(p, os.path.join(d, 'archive', stem + '_261106-1200' + ext))


# 1
reset(); T = w('W_x.md')
check('1a Write 既有 W_ 檔', tool('Write', T)[0], 2)
check('1b Write 不存在的 W_ 檔', tool('Write', os.path.join(WORK, 'W_new.md'))[0], 0)
# 2
reset(); T = w('W_x.md', mtime=time.time() - 1000)
check('2a Edit 無備份', tool('Edit', T)[0], 2)
backup(T)
check('2b Edit 有備份', tool('Edit', T)[0], 0)
# 3
os.utime(T, None)
check('3 放行後 mtime=現在，靠 state', tool('Edit', T)[0], 0)
# 4
st = json.load(open(os.path.join(STATE, 'w-colab-gate-state.json')))
at = max(st.values())
os.utime(T, (at + 1000, at + 1000))
check('4a 使用者後來編輯後 Edit', tool('Edit', T)[0], 2)
backup(T)
check('4b 再備份後 Edit', tool('Edit', T)[0], 0)
# 5
reset(); T = w('W_x.md'); w('a.txt')
check('5a cat | head', bash('cat W_x.md | head -3')[0], 0)
check('5b /usr/bin/grep', bash('/usr/bin/grep foo "W_x.md" && echo ok')[0], 0)
check('5c grep', bash('grep foo "W_x.md" && echo ok')[0], 0)
check('5d sed -n', bash("sed -n '1,5p' W_x.md")[0], 0)
# 6
check('6a python3 gen.py W_x.md', bash('python3 gen.py W_x.md')[0], 2)
check('6b echo > W_x.md', bash('echo hi > W_x.md')[0], 2)
check('6c sed -i', bash("sed -i '' 's/a/b/' W_x.md")[0], 2)
check('6d cat | tee', bash('cat a.txt | tee W_x.md')[0], 2)
# 7
reset(); T = w('W_x.md')
check('7 備份指令本身', bash('mkdir -p archive && cp -p W_x.md archive/W_x_261106-1200.md')[0], 0)
# 8
reset(); w('archive/W_old.md'); w('_待刪_2026-11-06/W_old.md'); w('notes.md')
check('8a Edit archive/W_old.md', tool('Edit', os.path.join(WORK, 'archive/W_old.md'))[0], 0)
check('8b Edit _待刪_/W_old.md', tool('Edit', os.path.join(WORK, '_待刪_2026-11-06/W_old.md'))[0], 0)
check('8c Edit notes.md', tool('Edit', os.path.join(WORK, 'notes.md'))[0], 0)
# 9
reset(); T = w('W_x.md')
check('9a 空 stdin', run(None, raw='')[0], 0)
check('9b 非 JSON', run(None, raw='not json{')[0], 0)
open(os.path.join(STATE, 'w-colab-gate.off'), 'w').close()
check('9c 關閉開關', tool('Write', T)[0], 0)
# 10
reset(); T = w('工作 檔/W_簡報.pptx', mtime=time.time() - 1000)
cmd = 'python3 x.py "%s"' % T
check('10a 中文空白路徑無備份', bash(cmd)[0], 2)
backup(T)
check('10b 備份後', bash(cmd)[0], 0)
# 11
reset(); T = w('W_x.md')
check('11a git add', bash('git add W_x.md')[0], 0)
check('11b git checkout --', bash('git checkout -- W_x.md')[0], 2)
# 12
reset(); w('sub/W_y.md')
check('12 cd sub && python3 gen.py', bash('cd sub && python3 gen.py W_y.md')[0], 2)
# 13
reset(); T = w('W_café_ぱ.md', mtime=time.time() - 1000)
T = unicodedata.normalize('NFC', T)
nfd = unicodedata.normalize('NFD', 'W_café_ぱ_261106-1200.md')
os.makedirs(os.path.join(WORK, 'archive'), exist_ok=True)
shutil.copy2(T, os.path.join(WORK, 'archive', nfd))
check('13 NFD 備份 vs NFC 目標', tool('Edit', T)[0], 0)
# 14
reset(); T = w('W_x.md'); w('other.md')
check('14 cp other.md W_x.md', bash('cp other.md W_x.md')[0], 2)
# 15
reset(); T = w('W_x.md', mtime=time.time() - 1000)
rc, err = tool('Edit', T)
m = re.search(r'備份指令：(.+)', err)
check('15a 取得退回的備份指令', bool(m) and rc == 2, True)
if m:
    check('15b 備份指令餵回 hook', bash(m.group(1))[0], 0)
    subprocess.run(m.group(1), shell=True, cwd=WORK)
    check('15c 執行備份後 Edit', tool('Edit', T)[0], 0)

# 16 備份比對收緊
for nm, want in (('W_x2_261106.md', 2), ('W_x_notes.txt', 2), ('261106_W_x.md', 0),
                 ('W_x_261106-1200.md', 0), ('W_x.md', 0)):
    reset(); T = w('W_x.md', mtime=time.time() - 1000)
    os.makedirs(os.path.join(WORK, 'archive'))
    shutil.copy2(T, os.path.join(WORK, 'archive', nm))
    check('16 archive 內 ' + nm, tool('Edit', T)[0], want)
# 17 括號 cd
reset(); w('sub/W_y.md')
check('17 (cd sub && python3 gen.py W_y.md)', bash('(cd sub && python3 gen.py W_y.md)')[0], 2)

# 18 退回訊息的相對／絕對路徑
reset(); T = w('sub dir/W_x.md', mtime=time.time() - 1000)
rc, err = tool('Edit', T)
m = re.search(r'備份指令：(.+)', err)
check('18a cwd 內：訊息不含 cwd 絕對路徑', rc == 2 and WORK not in err and bool(m), True)
if m:
    check('18b 相對備份指令餵回', bash(m.group(1))[0], 0)
    subprocess.run(m.group(1), shell=True, cwd=WORK)
    check('18c 執行後 Edit', tool('Edit', T)[0], 0)
reset(); OUT = os.path.join(BASE, 'outside'); shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT); T = os.path.join(OUT, 'W_o.md'); open(T, 'w').write('x'); os.utime(T, (time.time() - 1000,) * 2)
rc, err = tool('Edit', T)
m = re.search(r'備份指令：(.+)', err)
check('18d cwd 外：維持絕對路徑', rc == 2 and bool(m) and ('"' + OUT + '/archive"') in m.group(1), True)
if m:
    check('18e 絕對備份指令餵回', bash(m.group(1))[0], 0)

print('總計：%d PASS / %d FAIL' % (sum(res), len(res) - sum(res)))
sys.exit(0 if all(res) else 1)
