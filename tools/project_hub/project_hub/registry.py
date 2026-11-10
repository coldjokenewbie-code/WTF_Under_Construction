"""Machine-local enable registry; catalog reads only the declared Markdown table."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import socket
import unicodedata
from .errors import HubError
from .paths import project_id, trusted_root, no_symlinks, within
from .storage import atomic_json, locked, read_json


@dataclass(frozen=True)
class Project:
    project_id: str
    name: str
    root: Path
    data: Path

    def public(self):
        return dict(project_id=self.project_id, id=self.project_id, name=self.name, root=str(self.root))


def stable_id(name):
    return "p-" + hashlib.sha256(unicodedata.normalize("NFC", name).encode()).hexdigest()[:16]


def parse_catalog(path, machine):
    rows, column = [], None
    for line in no_symlinks(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == "project":
            column = cells.index(machine) if machine in cells else None
            continue
        if column is None or len(cells) <= column or cells[0].startswith("-"):
            continue
        paths = [value.strip() for value in cells[column].split("；") if value.strip().startswith("/")]
        working = [value for value in paths if "git_mirror" not in Path(value).parts]
        if not working and len(paths) == 1:
            working = paths
        if not working:
            continue
        rows.append(dict(candidate_id=stable_id(cells[0]), project_id=stable_id(cells[0]),
                         name=cells[0], root=working[0]))
    return rows


class Registry:
    def __init__(self, settings):
        self.path = no_symlinks(settings)
        self.reload()

    def reload(self):
        self.settings = read_json(self.path, {})
        if not isinstance(self.settings, dict):
            raise HubError("invalid_settings", "設定必須是物件")
        self.projects = [self.make_project(row, require_exists=False) for row in self.settings.get("projects", [])]
        self.validate(self.projects)

    @staticmethod
    def make_project(row, require_exists=True):
        identifier = project_id(row["project_id"])
        root = trusted_root(row["root"]) if require_exists else no_symlinks(Path(row["root"]).expanduser()).resolve()
        data = within(root, row.get("data_dir", "workingfiles/總控台"))
        return Project(identifier, row.get("name") or identifier, root, data)

    @staticmethod
    def validate(projects):
        if len({item.project_id for item in projects}) != len(projects):
            raise HubError("duplicate_id", "專案 ID 重複", 409)
        for index, item in enumerate(projects):
            for other in projects[index + 1:]:
                if item.root == other.root or item.root in other.root.parents or other.root in item.root.parents:
                    raise HubError("overlapping_root", "專案工作根目錄不得相同或為父子目錄", 409)

    def get(self, value):
        matches = [item for item in self.projects if value in (item.project_id, item.name)]
        if len(matches) != 1:
            raise HubError("project_not_found", "專案不存在或名稱不唯一", 404)
        return matches[0]

    def for_cwd(self, cwd):
        try:
            path = Path(cwd).resolve()
        except (TypeError, OSError):
            return None
        return next((item for item in self.projects if path == item.root or item.root in path.parents), None)

    def catalog(self):
        path = self.settings.get("registry_path")
        if not path:
            return []
        rows = parse_catalog(path, self.settings.get("machine", socket.gethostname()))
        for row in rows:
            existing = next((item for item in self.projects if str(item.root) == row["root"]), None)
            row.update(enabled=bool(existing), can_enable=False, reason="")
            if existing:
                row["project_id"] = existing.project_id
                row["reason"] = "已啟用"
                continue
            try:
                candidate = self.make_project(row)
                self.validate([*self.projects, candidate])
                row["can_enable"] = True
            except (HubError, OSError) as error:
                row["reason"] = str(error)
        return rows

    def register(self, identifier):
        with locked(self.path.parent):
            self.reload()
            row = next((row for row in self.catalog() if identifier in (row["candidate_id"], row["project_id"])), None)
            if row is None:
                raise HubError("candidate_not_found", "請選擇註冊表中的工作專案", 404)
            if row["enabled"]:
                return self.get(row["project_id"])
            if not row["can_enable"]:
                raise HubError("cannot_enable", row["reason"], 409)
            item = {key: row[key] for key in ("project_id", "name", "root")}
            self.settings.setdefault("projects", []).append(item)
            atomic_json(self.path, self.settings)
            self.reload()
            return self.get(row["project_id"])
