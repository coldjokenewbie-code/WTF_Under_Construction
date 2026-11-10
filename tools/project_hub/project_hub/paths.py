"""Validate paths before both reads and writes; never follow project symlinks."""
from pathlib import Path
import re
import unicodedata
from .errors import HubError


def no_symlinks(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise HubError("symlink", "路徑不可含符號連結", 403)
    return path


def trusted_root(value):
    path = no_symlinks(Path(value).expanduser())
    if not path.is_dir():
        raise HubError("root_missing", "專案工作根目錄不存在")
    return path.resolve()


def within(root, relative, public=False):
    root = no_symlinks(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise HubError("path_escape", "只接受專案內相對路徑", 403)
    if public and any(part.startswith((".", "~$")) for part in relative.parts):
        raise HubError("hidden_path", "不提供隱藏檔案或目錄", 403)
    path = no_symlinks(root / relative)
    if path != root and root not in path.resolve().parents:
        raise HubError("path_escape", "路徑超出專案", 403)
    return path


def exhibit_name(value):
    if not isinstance(value, str) or not value.strip() or value in (".", ".."):
        raise HubError("invalid_exhibit", "工作項目名稱不可為空白")
    if value != value.strip() or re.search(r'[/\\:*?"<>|\x00-\x1f\u200b]', value):
        raise HubError("invalid_exhibit", "工作項目名稱含不支援字元")
    if len(value) > 160:
        raise HubError("invalid_exhibit", "工作項目名稱過長")
    return value


def name_key(value):
    return unicodedata.normalize("NFC", value).casefold()


def project_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", value):
        raise HubError("invalid_project_id", "專案 ID 格式無效")
    return value
