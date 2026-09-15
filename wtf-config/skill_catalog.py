"""WTF skill metadata、備援索引與實體副本驗證；不做語意觸發判斷。"""

import json
import re
import shutil
from pathlib import Path


def _scalar(value, path):
    """接受純文字與單/雙引號 scalar；其他 YAML 結構需明確報錯。"""
    if value.startswith('"'):
        try:
            result = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}: 非法雙引號 metadata") from error
        if not isinstance(result, str):
            raise ValueError(f"{path}: metadata 必須是文字")
        return result
    if value.startswith("'"):
        if not value.endswith("'") or len(value) < 2:
            raise ValueError(f"{path}: 單引號未關閉")
        return value[1:-1].replace("''", "'")
    if value.startswith(("[", "{", "&", "*", "!")):
        raise ValueError(f"{path}: name/description 僅支援文字 scalar")
    return value


def read_metadata(path):
    """讀 name/description；支援單行或 |/> 多行，不引入 YAML 依賴。"""
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        raise ValueError(f"{path}: 缺 frontmatter")
    lines = match.group(1).splitlines()
    metadata = {}
    for position, line in enumerate(lines):
        field = re.match(r"^(name|description):\s*(.*)$", line)
        if not field:
            continue
        key, value = field.groups()
        if key in metadata:
            raise ValueError(f"{path}: 重複欄位 {key}")
        if value in ("|", ">", "|-", ">-", "|+", ">+"):
            block = []
            for following in lines[position + 1:]:
                if following and not following[0].isspace():
                    break
                block.append(following.strip())
            value = " ".join(block)
        else:
            value = _scalar(value.strip(), path)
        metadata[key] = " ".join(value.split())
    for key in ("name", "description"):
        if not metadata.get(key):
            raise ValueError(f"{path}: 缺少或空白 {key}")
    return metadata


def read_skills(source):
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"{source}: skill SSOT 必須是實體目錄")
    skills, names = [], set()
    for directory in sorted(source.iterdir()):
        if not directory.is_dir() or directory.name.startswith("."):
            continue
        path = directory / "SKILL.md"
        if directory.is_symlink() or any(item.is_symlink() for item in directory.rglob("*")):
            raise ValueError(f"{directory}: SSOT 不允許 symlink")
        metadata = read_metadata(path) if path.is_file() else None
        if metadata is None:
            raise ValueError(f"{path}: 缺 SKILL.md")
        key = metadata["name"].casefold()
        if key in names:
            raise ValueError(f"{path}: 同層重名 skill {metadata['name']}")
        names.add(key)
        skills.append(dict(metadata, directory=directory))
    return skills


def _cell(value):
    return str(value).replace("&", "&amp;").replace("|", "&#124;").replace("`", "&#96;").replace("<", "&lt;").replace(">", "&gt;")


def render_index(source, index_root, relative_to=None):
    skills = read_skills(source)
    source_label = source.relative_to(relative_to) if relative_to else source.absolute()
    lines = [f"<!-- 由 sync_config.py 產生，勿手改；來源 SSOT: {_cell(source_label)} -->",
             "# WTF skill 備援索引", "",
             "僅列 SSOT metadata。原生清單可用時不必重讀；同名專案優先。",
             "description 是觸發描述，命中才讀 SKILL.md；索引不保證模型會執行。",
             "path 相對專案根解析；絕對路徑則為本機部署位置。", "",
             "| name | description | path |", "|---|---|---|"]
    for skill in skills:
        path = index_root / skill["directory"].name / "SKILL.md"
        path = path.relative_to(relative_to) if relative_to else path.absolute()
        lines.append(f"| {_cell(skill['name'])} | {_cell(skill['description'])} | `{_cell(path)}` |")
    return "\n".join(lines) + "\n"


def _make_directory(path):
    if path.is_symlink():
        path.unlink()
    path.mkdir(parents=True, exist_ok=True)


def _copy_skill(source, destination):
    _make_directory(destination)
    for item in sorted(source.rglob("*")):
        target = destination / item.relative_to(source)
        if item.is_dir():
            _make_directory(target)
        elif item.is_file():
            if target.is_symlink():
                target.unlink()
            shutil.copy2(item, target)


def deploy_skill_set(source, destination, index_path, index_root=None, relative_to=None):
    skills = read_skills(source)
    content = render_index(source, index_root or destination, relative_to)
    _make_directory(destination)
    for skill in skills:
        _copy_skill(skill["directory"], destination / skill["directory"].name)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if index_path.is_symlink():
        index_path.unlink()
    index_path.write_text(content, encoding="utf-8")
    return [f"  v 寫入 {destination}（{len(skills)} 個 SSOT skill；只新增/覆蓋，不刪額外目錄）",
            f"  v 寫入 {index_path}"]


def _skill_errors(skill, destination):
    source = skill["directory"]
    target = destination / source.name
    errors = []
    if target.is_symlink() or not target.is_dir():
        return [f"{target}: 缺實體 skill 目錄"]
    for item in sorted(source.rglob("*")):
        deployed = target / item.relative_to(source)
        if item.is_dir():
            if deployed.is_symlink() or not deployed.is_dir():
                errors.append(f"{deployed}: 缺實體子目錄")
        elif item.is_file():
            if deployed.is_symlink() or not deployed.is_file() or item.read_bytes() != deployed.read_bytes():
                errors.append(f"{deployed}: 缺檔、symlink 或內容過期")
    return errors


def check_skill_set(source, destination, index_path, index_root=None, relative_to=None):
    try:
        skills = read_skills(source)
        expected = render_index(source, index_root or destination, relative_to)
    except (ValueError, OSError) as error:
        return True, [f"  x [INVALID] {error}"]
    errors, notes = [], []
    if destination.is_symlink() or not destination.is_dir():
        errors.append(f"{destination}: 缺實體 skills 目錄")
    else:
        for skill in skills:
            errors.extend(_skill_errors(skill, destination))
        known = {skill["directory"].name for skill in skills}
        extra = sorted(item.name for item in destination.iterdir() if item.name not in known)
        if extra:
            notes.append(f"  ! [EXTRA  ] {destination}: {', '.join(extra)}（非 SSOT／可能退役；保留，不判失效）")
    if index_path.is_symlink() or not index_path.is_file() or index_path.read_bytes() != expected.encode("utf-8"):
        errors.append(f"{index_path}: 索引缺失或內容過期")
    for skill in skills:
        if skill["name"] != skill["directory"].name:
            notes.append(f"  ! [NAME   ] {skill['directory']}: name={skill['name']} 與資料夾不同")
    notes.extend(f"  x [STALE  ] {error}" for error in errors)
    if not errors:
        file_count = sum(item.is_file() for skill in skills for item in skill["directory"].rglob("*"))
        notes.append(f"  v [OK     ] {destination}（{len(skills)} skills／{file_count} 檔內容＋索引）")
    return bool(errors), notes
