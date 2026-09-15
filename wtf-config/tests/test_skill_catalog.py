import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill_catalog import check_skill_set, deploy_skill_set, read_metadata, read_skills, render_index


class SkillCatalogTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "中文 project"
        self.source = self.root / "._agents/skills"
        self.destination = self.root / ".agents/skills"
        self.index = self.root / "._agents/skills-index.md"
        self.skill = self.source / "handover"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: handover\ndescription: 交接、換人接續 | handover\n---\n保留完整本文\n")
        (self.skill / "scripts").mkdir()
        (self.skill / "scripts/check.py").write_text("print('check')\n")
        self.arguments = dict(source=self.source, destination=self.destination, index_path=self.index,
                              index_root=self.source, relative_to=self.root)

    def test_project_index_is_portable_and_metadata_only(self):
        deploy_skill_set(**self.arguments)
        text = self.index.read_text()
        self.assertIn("._agents/skills/handover/SKILL.md", text)
        self.assertNotIn(str(self.root), text)
        self.assertNotIn("保留完整本文", text)
        self.assertIn("&#124;", text)
        self.assertFalse(check_skill_set(**self.arguments)[0])

    def test_global_index_uses_deployed_absolute_path(self):
        text = render_index(self.source, self.destination)
        self.assertIn(str(self.destination / "handover/SKILL.md"), text)
        self.assertNotIn("保留完整本文", text)

    def test_sync_preserves_foreign_skills_and_is_idempotent(self):
        for name in ("local-skill", ".system", "retired-wtf"):
            directory = self.destination / name
            directory.mkdir(parents=True)
            (directory / "sentinel").write_bytes(b"must survive")
        external = self.root / "external"
        external.mkdir()
        (self.destination / "find-skills").symlink_to(external, target_is_directory=True)
        deploy_skill_set(**self.arguments)
        before = {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        deploy_skill_set(**self.arguments)
        after = {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertTrue((self.destination / "find-skills").is_symlink())
        has_error, notes = check_skill_set(**self.arguments)
        self.assertFalse(has_error)
        self.assertIn("EXTRA", "\n".join(notes))

    def test_drift_missing_support_file_and_index_are_detected(self):
        deploy_skill_set(**self.arguments)
        (self.destination / "handover/SKILL.md").write_text("changed")
        self.assertTrue(check_skill_set(**self.arguments)[0])
        deploy_skill_set(**self.arguments)
        (self.destination / "handover/scripts/check.py").unlink()
        self.assertTrue(check_skill_set(**self.arguments)[0])
        deploy_skill_set(**self.arguments)
        self.index.write_text(self.index.read_text().replace("換人接續", "wrong"))
        self.assertTrue(check_skill_set(**self.arguments)[0])

    def test_missing_duplicate_metadata_and_duplicate_names_fail(self):
        path = self.skill / "SKILL.md"
        for header in ("name: handover", "name: handover\nname: again\ndescription: x"):
            path.write_text(f"---\n{header}\n---\nbody")
            with self.assertRaises(ValueError):
                read_skills(self.source)
        path.write_text("---\nname: handover\ndescription: x\n---\nbody")
        duplicate = self.source / "other"
        duplicate.mkdir()
        (duplicate / "SKILL.md").write_bytes(path.read_bytes())
        with self.assertRaises(ValueError):
            read_skills(self.source)

    def test_block_and_quoted_descriptions(self):
        path = self.skill / "SKILL.md"
        for value in ('>\n  請交接\n  換人接續', '"請交接 換人接續"', "'請交接 換人接續'"):
            path.write_text(f"---\nname: handover\ndescription: {value}\n---\nbody")
            self.assertEqual("請交接 換人接續", read_metadata(path)["description"])

    def test_owned_symlink_is_replaced_without_writing_external_target(self):
        self.destination.mkdir(parents=True)
        external = self.root / "external"
        external.mkdir()
        (external / "SKILL.md").write_text("external original")
        (self.destination / "handover").symlink_to(external, target_is_directory=True)
        deploy_skill_set(**self.arguments)
        self.assertFalse((self.destination / "handover").is_symlink())
        self.assertEqual("external original", (external / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
