"""用暫存家目錄及 registry 呼叫真實 cmd_sync/cmd_check，不修改使用者環境。"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1]
RUNNER = '''
import importlib.util, sys
from pathlib import Path
from unittest.mock import patch
fixture = Path(sys.argv[1])
sys.path.insert(0, str(fixture / 'repo/wtf-config'))
with patch('pathlib.Path.home', return_value=fixture / 'home'):
    spec = importlib.util.spec_from_file_location('sync_config', fixture / 'repo/wtf-config/sync_config.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.registry_dirs = lambda: [fixture / 'project']
    sys.argv = ['sync_config.py', sys.argv[2]]
    raise SystemExit(module.main())
'''


class SyncSkillsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = self.root / "repo/wtf-config"
        self.config.mkdir(parents=True)
        for name in ("sync_config.py", "skill_catalog.py", "GLOBAL.md", "AGENTS.md", "CLAUDE_CODE.md", "CODEX.md", "GEMINI.md"):
            shutil.copy2(CONFIG / name, self.config / name)
        shutil.copytree(CONFIG / "hooks", self.config / "hooks")
        shutil.copytree(CONFIG / "skills", self.config / "skills")
        for tool in (".claude", ".codex", ".gemini"):
            (self.root / "home" / tool).mkdir(parents=True)
        source = self.root / "project/._agents/skills/handover"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("---\nname: handover\ndescription: 專案交接優先\n---\nproject body\n")
        self.runner = self.root / "run.py"
        self.runner.write_text(RUNNER)

    def run_sync(self, action="sync", expected=0):
        result = subprocess.run([sys.executable, str(self.runner), str(self.root), action],
                                text=True, capture_output=True)
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result.stdout

    def snapshot(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for base in (self.root / "home", self.root / "project")
                for path in base.rglob("*") if path.is_file()}

    def test_full_sync_twice_bundle_and_project_override(self):
        self.run_sync()
        before = self.snapshot()
        self.run_sync()
        self.assertEqual(before, self.snapshot())
        output = self.run_sync("check")
        skill_count = len(list((self.config / "skills").glob("*/SKILL.md")))
        self.assertGreater(skill_count, 0)
        self.assertIn(f"{skill_count} skills", output)
        self.assertIn("session bundle import SHA/manifest/SSOT 三者一致", output)
        self.assertIn("._agents/skills/handover/SKILL.md", (self.root / "project/._agents/skills-index.md").read_text())
        for relative in (".claude/skills", ".agents/skills"):
            self.assertIn("project body", (self.root / "project" / relative / "handover/SKILL.md").read_text())

    def test_corruption_missing_files_and_duplicate_name_exit_one(self):
        self.run_sync()
        paths = [self.root / "home/.codex/skills/handover/SKILL.md",
                 self.root / "home/.gemini/wtf-skills-index.md",
                 self.root / "project/.agents/skills/handover/SKILL.md",
                 self.root / "home/.claude/skills/ai-team/AGENT_SPEC_TEMPLATE.md",
                 self.root / "home/.codex/AGENTS.md"]
        for path in paths:
            with self.subTest(path=path):
                before = path.read_bytes()
                path.write_bytes(before + b"corruption")
                self.run_sync("check", expected=1)
                path.unlink()
                self.run_sync("check", expected=1)
                self.run_sync()
        duplicate = self.config / "skills/duplicate"
        shutil.copytree(self.config / "skills/handover", duplicate)
        before = self.snapshot()
        self.run_sync("check", expected=1)
        self.run_sync("sync", expected=1)
        self.assertEqual(before, self.snapshot(), "invalid metadata must fail before mutation")

    def test_extra_skills_survive_and_absent_tool_skips(self):
        local = self.root / "home/.claude/skills/user-owned"
        local.mkdir(parents=True)
        (local / "sentinel").write_text("retain")
        shutil.rmtree(self.root / "home/.gemini")
        output = self.run_sync()
        self.assertIn("EXTRA", output)
        self.assertIn("SKIP", output)
        self.assertFalse((self.root / "home/.gemini").exists())
        self.assertEqual("retain", (local / "sentinel").read_text())

    def test_claude_bundle_failure_reaches_exit_status(self):
        self.run_sync()
        bundle = next((self.root / "home/.claude/wtf-session-bundles").iterdir())
        (bundle / "GLOBAL.md").write_text("wrong")
        self.run_sync("check", expected=1)

    def test_removed_bundle_import_does_not_pass_check(self):
        self.run_sync()
        shutil.copy2(self.config / "CLAUDE_CODE.md", self.root / "home/.claude/CLAUDE.md")
        self.run_sync("check", expected=1)


if __name__ == "__main__":
    unittest.main()
