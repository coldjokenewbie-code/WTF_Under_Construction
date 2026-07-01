"""Policy Gate — 雙層安全閘（建構前 check_command + 執行前 executor 重檢）。

預設拒絕原則（default-deny 的精神）：
- 網路操作：除非 task constraints.allow_network=True，否則拒 curl/wget/ssh/scp/nc/git push…
- 破壞性操作：rm -rf、git reset --hard、git push、dd、mkfs、chmod -R、:(){ 等
- 命令注入：argv 必須是 list（禁 shell=True）；任一 token 含 shell 元字元即拒
- 寫入邊界：只能寫 constraints.write_allowlist 內目錄（相對 framework 根）
"""
from __future__ import annotations
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .paths import ASSISTANT_ROOT, DATA_DIR, OUTPUTS_DIR

# 網路類執行檔（allow_network=False 時拒）
NETWORK_BINS = {"curl", "wget", "ssh", "scp", "sftp", "nc", "ncat", "telnet", "rsync"}
# 破壞性 / 外送 token 模式（任何時候都拒，與 allow 旗標無關）
DESTRUCTIVE_PATTERNS = [
    re.compile(r"^rm$"),
    re.compile(r"^dd$"),
    re.compile(r"^mkfs"),
    re.compile(r"^shutdown$"),
    re.compile(r"^reboot$"),
]
# git 子命令黑名單（會改遠端/歷史/工作區，任何時候都拒）
GIT_FORBIDDEN_SUB = {"push", "reset", "clean", "rebase", "filter-branch"}
# git 網路子命令（allow_network=False 時拒）—— 修補 Agy 驗收發現 #2
GIT_NETWORK_SUB = {"clone", "pull", "fetch", "remote", "submodule", "ls-remote"}
# 直譯器（搭配寫入區腳本 = 拒）—— 修補 Agy 驗收發現 #1 write-then-execute
_INTERP_EXACT = {"sh", "bash", "zsh", "fish", "env", "osascript", "awk"}
_INTERP_PREFIX = ("python", "node", "perl", "ruby", "php", "deno", "bun")
# 腳本副檔名：直譯器只擋「寫入區的腳本檔」，不誤殺傳入的 data/輸出目錄參數
_SCRIPT_EXTS = {".py", ".js", ".mjs", ".cjs", ".ts", ".sh", ".bash", ".zsh", ".rb", ".pl", ".php"}
# shell 元字元（出現在任一 argv token = 疑似注入）
SHELL_METACHARS = re.compile(r"[;&|`$><\n]|\$\(|\.\.")


@dataclass
class Decision:
    allow: bool
    reason: str


def _is_interpreter(name: str) -> bool:
    return name in _INTERP_EXACT or name.startswith(_INTERP_PREFIX)


def _real_name(token: str) -> str:
    """解析真實執行檔 basename（反 symlink/別名改名）—— 修補 Agy 驗收發現 #3。"""
    resolved = shutil.which(token) or token
    try:
        return Path(os.path.realpath(resolved)).name
    except (OSError, RuntimeError):
        return Path(token).name


def _under(path_str: str, roots: list[Path]) -> bool:
    try:
        rp = Path(path_str).resolve()
    except (OSError, RuntimeError):
        return False
    for r in roots:
        try:
            rp.relative_to(r.resolve())
            return True
        except ValueError:
            continue
    return False


def check_command(argv: list[str], *, allow_network: bool = False) -> Decision:
    """建構前檢查一條待執行命令（argv list）。"""
    if not isinstance(argv, list) or not argv:
        return Decision(False, "argv 必須是非空 list（禁 shell=True / 字串命令）")
    if not all(isinstance(t, str) for t in argv):
        return Decision(False, "argv 每個 token 必須是字串")

    for tok in argv:
        if SHELL_METACHARS.search(tok):
            return Decision(False, f"token 含 shell 元字元/路徑穿越，疑似注入：{tok!r}")

    bin_name = Path(argv[0]).name
    real_name = _real_name(argv[0])
    exec_forbidden = [DATA_DIR, OUTPUTS_DIR]

    # 同時用「表面名」與「真實名」比黑名單（反 symlink/別名）
    for nm in {bin_name, real_name}:
        for pat in DESTRUCTIVE_PATTERNS:
            if pat.match(nm):
                return Decision(False, f"破壞性命令被拒：{nm}（real={real_name}）")
        if nm in NETWORK_BINS and not allow_network:
            return Decision(False, f"網路命令被拒（allow_network=False）：{nm}")

    # 禁止「執行寫入區（data/outputs）內的檔案」—— 擋 write-then-execute
    if _under(argv[0], exec_forbidden):
        return Decision(False, f"禁止執行寫入區內的檔案：{argv[0]}")

    # 直譯器 + 寫入區「腳本檔」= 拒（如 python3 outputs/x.py）；data/輸出目錄參數不誤殺
    if _is_interpreter(bin_name) or _is_interpreter(real_name):
        for a in argv[1:]:
            if a.startswith("-"):
                continue
            if Path(a).suffix.lower() in _SCRIPT_EXTS and _under(a, exec_forbidden):
                return Decision(False, f"禁止以直譯器執行寫入區腳本：{a}")

    if bin_name == "git" or real_name == "git":
        # 用全 token 集合比對：避開 `git -C <dir> <sub>` 把 dir 誤認成子命令
        tokens = set(argv[1:])
        hit_forbidden = tokens & GIT_FORBIDDEN_SUB
        if hit_forbidden:
            return Decision(False, f"git {sorted(hit_forbidden)[0]} 被拒（改遠端/歷史/工作區）")
        hit_network = tokens & GIT_NETWORK_SUB
        if hit_network and not allow_network:
            return Decision(False, f"git {sorted(hit_network)[0]} 被拒（網路操作，allow_network=False）")

    return Decision(True, "ok")


def resolve_write_target(rel_or_abs: str, write_allowlist: list[str]) -> Path:
    """把欲寫入路徑解析為絕對路徑並驗證在白名單目錄內；違規即 raise。"""
    allow_roots = [(ASSISTANT_ROOT / a).resolve() for a in (write_allowlist or [])]
    p = Path(rel_or_abs)
    target = p if p.is_absolute() else (ASSISTANT_ROOT / p)
    target = target.resolve()
    for root in allow_roots:
        try:
            target.relative_to(root)
            return target
        except ValueError:
            continue
    raise PermissionError(f"寫入目標 {target} 不在白名單 {[str(r) for r in allow_roots]} 內")


def check_read_path(abs_path: str, read_roots: list[Path]) -> Decision:
    """確認唯讀掃描的路徑落在已登記的 root 內（反路徑穿越）。"""
    try:
        target = Path(abs_path).resolve()
    except (OSError, RuntimeError) as e:
        return Decision(False, f"路徑解析失敗：{e}")
    for root in read_roots:
        try:
            target.relative_to(root.resolve())
            return Decision(True, "ok")
        except ValueError:
            continue
    return Decision(False, f"讀取路徑 {target} 不在已登記 root 內")
