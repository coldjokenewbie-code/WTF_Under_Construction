#!/usr/bin/env python3
"""審閱頁交付：Edge 已開著同一頁就重新整理該分頁（實測不搶前景）；沒開著就 open -g 開新分頁，並立刻把前景還給原本的 app。
2026-11-01 實測（Edge 156）：open -g、AppleScript 新增分頁、改分頁網址都會讓 Edge 跳到前景；只有 reload 不會。
開完立刻 open -b 原 app，Edge 只在前景約 0.05 秒。
用法：python3 reload_or_open.py <html 絕對或相對路徑>"""
import os, subprocess, sys, urllib.parse

def tabs():
    script = ('set out to ""\n'
              'tell application "Microsoft Edge"\n'
              ' repeat with w from 1 to count of windows\n'
              '  repeat with t from 1 to count of tabs of window w\n'
              '   set out to out & w & "\t" & t & "\t" & (URL of tab t of window w) & linefeed\n'
              '  end repeat\n end repeat\nend tell\nreturn out')
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else []

def main(path):
    target = os.path.realpath(path)
    for line in tabs():
        parts = line.split('\t')
        if len(parts) < 3 or not parts[2].startswith('file://'):
            continue
        p = urllib.parse.unquote(urllib.parse.urlparse(parts[2]).path)
        if os.path.realpath(p) == target:
            w, t = parts[0], parts[1]
            subprocess.run(['osascript', '-e', f'tell application "Microsoft Edge" to reload tab {t} of window {w}'])
            print(f'reloaded window {w} tab {t}')
            return
    front = subprocess.run(['lsappinfo', 'info', '-only', 'bundleID', subprocess.run(['lsappinfo', 'front'], capture_output=True, text=True).stdout.strip()],
                           capture_output=True, text=True).stdout.split('"')
    prev = front[3] if len(front) > 3 else ''
    subprocess.run(['/usr/bin/open', '-g', target])
    if prev and prev != 'com.microsoft.edgemac':
        subprocess.run(['/usr/bin/open', '-b', prev])
    print(f'opened new (前景還給 {prev or "未知"})')

if __name__ == '__main__':
    main(sys.argv[1])
