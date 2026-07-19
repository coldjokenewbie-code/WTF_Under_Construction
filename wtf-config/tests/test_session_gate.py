from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "wtf-config" / "hooks"
GATE = HOOKS / "wtf-session-gate.py"
WRAPPER = HOOKS / "wtf-session-gate.sh"
POLICY = ROOT / "wtf-config" / "policies" / "session-policy.json"
SPEC = importlib.util.spec_from_file_location("wtf_bundle", HOOKS / "wtf_bundle.py")
BUNDLE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(BUNDLE)


class SessionGateTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name)
        source_dir = self.home / "sources"
        source_dir.mkdir()
        self.global_source = source_dir / "GLOBAL.md"
        self.agents_source = source_dir / "AGENTS.md"
        self.global_source.write_text("global one\nglobal two\n", encoding="utf-8")
        self.agents_source.write_text("agents one\nagents two\n", encoding="utf-8")
        self.bundle = BUNDLE.create_bundle(self.global_source, self.agents_source, self.home)
        self.bundle_hash = self.bundle.name
        self.base = {"session_id": "session-1", "bundle_sha256": self.bundle_hash}
        self.env = os.environ.copy()
        self.env.update({"WTF_GATE_HOME": str(self.home), "WTF_GATE_POLICY": str(POLICY)})
        self.run_gate("init", self.base, expected=0)

    def tearDown(self):
        self.temporary.cleanup()

    def run_gate(self, command, event=None, raw=None, expected=None, extra_env=None):
        environment = dict(self.env)
        if extra_env:
            environment.update(extra_env)
        data = raw if raw is not None else json.dumps(event or {})
        result = subprocess.run([sys.executable, str(GATE), command], input=data,
                                text=True, capture_output=True, env=environment)
        if expected is not None:
            self.assertEqual(expected, result.returncode, result.stderr)
        return result

    def output(self, result):
        return json.loads(result.stdout) if result.stdout.strip() else None

    def sign(self, name, event=None, parent_marker=False):
        payload = dict(self.base if event is None else event)
        payload.update({"file_path": str(self.bundle / name), "load_reason": "include"})
        if parent_marker:
            payload["parent_file_path"] = str(self.home / ".claude" / "CLAUDE.md")
        return self.run_gate("instructions", payload)

    def pretool(self, tool_name="Bash", tool_input=None, event=None):
        payload = dict(self.base if event is None else event)
        payload.update({"tool_name": tool_name, "tool_input": tool_input or {"command": "true"}})
        return self.run_gate("pretool", payload, expected=0)

    def assert_denied(self, result):
        value = self.output(result)
        self.assertEqual("deny", value["hookSpecificOutput"]["permissionDecision"])

    def recovery_event(self, name, **updates):
        event = dict(self.base)
        event.update({"tool_name": "Read", "tool_input": {"file_path": str(self.bundle / name)}})
        event["tool_input"].update(updates)
        return event

    def test_two_receipts_are_required_before_allow(self):
        self.assertEqual(0, self.sign("GLOBAL.md").returncode)
        self.assert_denied(self.pretool())
        self.assertEqual(0, self.sign("AGENTS.md", parent_marker=True).returncode)
        self.assertIsNone(self.output(self.pretool()))

    def test_partial_reads_are_denied_and_never_signed(self):
        offset = self.pretool("Read", self.recovery_event("GLOBAL.md", offset=2)["tool_input"])
        small = self.pretool("Read", self.recovery_event("GLOBAL.md", limit=1)["tool_input"])
        self.assert_denied(offset)
        self.assert_denied(small)
        post = self.recovery_event("GLOBAL.md", offset=2)
        post["tool_response"] = {"success": True}
        self.assertEqual(2, self.run_gate("postread", post).returncode)
        self.assertFalse((self.state() / "GLOBAL.receipt.json").exists())

    def test_similar_name_tampered_receipt_and_changed_source_fail(self):
        similar = self.bundle / "GLOBAL-copy.md"
        similar.write_bytes((self.bundle / "GLOBAL.md").read_bytes())
        bad = dict(self.base, file_path=str(similar), load_reason="include")
        self.assertEqual(2, self.run_gate("instructions", bad).returncode)
        self.sign("GLOBAL.md")
        self.sign("AGENTS.md")
        receipt_path = self.state() / "GLOBAL.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["source_sha256"] = "0" * 64
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        self.assert_denied(self.pretool())
        self.sign("GLOBAL.md")
        changed = bytearray((self.bundle / "AGENTS.md").read_bytes())
        changed[0] ^= 1
        (self.bundle / "AGENTS.md").write_bytes(changed)
        self.assert_denied(self.pretool())

    def test_generation_change_invalidates_old_receipts(self):
        self.sign("GLOBAL.md")
        self.sign("AGENTS.md")
        old = json.loads((self.state() / "generation.json").read_text())["generation"]
        # 換代由 resume/compact 觸發；startup init 對既有 generation 不旋轉（修並行競態的關鍵）
        self.run_gate("init", {**self.base, "source": "resume"}, expected=0)
        new = json.loads((self.state() / "generation.json").read_text())["generation"]
        self.assertNotEqual(old, new)
        self.assert_denied(self.pretool())

    def test_startup_init_does_not_rotate_existing_generation(self):
        self.sign("GLOBAL.md")
        self.sign("AGENTS.md")
        old = json.loads((self.state() / "generation.json").read_text())["generation"]
        self.run_gate("init", {**self.base, "source": "startup"}, expected=0)
        new = json.loads((self.state() / "generation.json").read_text())["generation"]
        self.assertEqual(old, new)  # startup 不覆蓋 → 收據仍有效
        self.assertIsNone(self.output(self.pretool()))

    def test_agent_cannot_borrow_main_receipts(self):
        self.sign("GLOBAL.md")
        self.sign("AGENTS.md")
        agent = dict(self.base, agent_key="agent-A")
        self.run_gate("init-agent", agent, expected=0)
        self.assert_denied(self.pretool(event=agent))
        self.assertIsNone(self.output(self.pretool()))
        self.assertEqual(0, self.run_gate("stop-agent", agent).returncode)
        missing_key = self.run_gate("stop-agent", self.base, expected=0)
        self.assertEqual("block", self.output(missing_key)["decision"])

    def test_recovery_is_once_per_generation_and_source(self):
        event = self.recovery_event("GLOBAL.md")
        self.assertIsNone(self.output(self.run_gate("pretool", event, expected=0)))
        event["tool_response"] = {"is_error": True}
        self.assertEqual(2, self.run_gate("postread", event).returncode)
        self.assertFalse((self.state() / "GLOBAL.receipt.json").exists())
        event["tool_response"] = {"success": True}
        self.assertEqual(0, self.run_gate("postread", event).returncode)
        self.assertTrue((self.state() / "GLOBAL.receipt.json").exists())
        self.assert_denied(self.run_gate("pretool", event, expected=0))

    def test_consecutive_generation_recovery_fuses(self):
        first = self.recovery_event("GLOBAL.md")
        self.assertIsNone(self.output(self.run_gate("pretool", first, expected=0)))
        self.run_gate("init", self.base, expected=0)
        second = self.recovery_event("GLOBAL.md")
        self.assert_denied(self.run_gate("pretool", second, expected=0))
        recovery = json.loads((self.state() / "recovery.json").read_text())
        self.assertTrue(recovery["fused"])

    def test_stop_blocks_without_receipts_even_when_hook_active(self):
        plain = self.run_gate("stop", self.base, expected=0)
        active = self.run_gate("stop", dict(self.base, stop_hook_active=True), expected=0)
        self.assertEqual("block", self.output(plain)["decision"])
        self.assertEqual("block", self.output(active)["decision"])

    def test_protected_paths_are_denied_after_receipts(self):
        self.sign("GLOBAL.md")
        self.sign("AGENTS.md")
        targets = [self.home / ".claude" / "settings.json",
                   self.home / ".claude" / "wtf-session-state" / "x",
                   self.home / ".claude" / "wtf-session-bundles" / "x"]
        for target in targets:
            with self.subTest(target=target):
                self.assert_denied(self.pretool("Write", {"file_path": str(target), "content": "{}"}))

    def test_malformed_json_fails_closed(self):
        result = self.run_gate("pretool", raw="{broken", expected=0)
        self.assert_denied(result)
        self.assertIn("malformed hook JSON", result.stderr)

    def test_bypass_writes_audit_warning(self):
        result = self.run_gate("pretool", self.base, expected=0,
                               extra_env={"WTF_SESSION_GATE_BYPASS": "1"})
        self.assertIsNone(self.output(result))
        audits = list(self.state().glob("audit-warning-*.json"))
        self.assertEqual(1, len(audits))
        self.assertIn("BYPASS=1", audits[0].read_text(encoding="utf-8"))

    def test_bundle_is_immutable_and_manifest_hashes_validate(self):
        manifest_bytes = (self.bundle / "manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        self.assertEqual(self.bundle_hash, hashlib.sha256(manifest_bytes).hexdigest())
        for name, record in manifest["sources"].items():
            data = (self.bundle / name).read_bytes()
            self.assertEqual(record["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(record["bytes"], len(data))
            self.assertEqual(record["lines"], len(data.splitlines()))
        before = (self.bundle / "manifest.json").stat().st_mtime_ns
        self.assertEqual(self.bundle, BUNDLE.create_bundle(
            self.global_source, self.agents_source, self.home))
        self.assertEqual(before, (self.bundle / "manifest.json").stat().st_mtime_ns)
        (self.bundle / "GLOBAL.md").write_text("tampered", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            BUNDLE.create_bundle(self.global_source, self.agents_source, self.home)

    def test_manifest_tamper_prevents_generation(self):
        manifest_path = self.bundle / "manifest.json"
        manifest_path.write_bytes(manifest_path.read_bytes() + b" ")
        self.assertEqual(2, self.run_gate("init", self.base).returncode)

    def test_parent_path_is_feature_detected(self):
        self.assertEqual(0, self.sign("GLOBAL.md").returncode)
        bad = dict(self.base, file_path=str(self.bundle / "AGENTS.md"), load_reason="include",
                   parent_file_path=str(self.home / "wrong.md"))
        self.assertEqual(2, self.run_gate("instructions", bad).returncode)
        bad["load_reason"] = "future-reason"
        self.assertEqual(2, self.run_gate("instructions", bad).returncode)

    def test_dispatcher_preserves_gate_block_when_stop_hook_is_active(self):
        payload = dict(self.base, stop_hook_active=True)
        result = subprocess.run([sys.executable, str(HOOKS / "stop_dispatcher.py")],
                                input=json.dumps(payload), text=True, capture_output=True, env=self.env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("block", json.loads(result.stdout)["decision"])

    def test_bundle_size_and_line_limits_fail(self):
        with self.assertRaises(ValueError):
            BUNDLE.create_bundle(self.global_source, self.agents_source, self.home,
                                 max_source_bytes=1)
        with self.assertRaises(ValueError):
            BUNDLE.create_bundle(self.global_source, self.agents_source, self.home,
                                 max_source_lines=1)

    def test_wrapper_exits_two_when_python_is_unavailable(self):
        result = subprocess.run(["/bin/sh", str(WRAPPER), "pretool"], input="{}", text=True,
                                capture_output=True, env={"PATH": ""})
        self.assertEqual(2, result.returncode)
        self.assertIn("python3 and python are unavailable", result.stderr)

    def state(self, agent="main"):
        return self.home / ".claude" / "wtf-session-state" / "session-1" / agent

    def race_state(self, session):
        return self.home / ".claude" / "wtf-session-state" / session / "main"

    def test_instructions_before_init_self_creates_generation_and_survives_startup_init(self):
        event = {"session_id": "race-1", "bundle_sha256": self.bundle_hash}
        for name in ("GLOBAL.md", "AGENTS.md"):
            payload = dict(event)
            payload.update({"file_path": str(self.bundle / name), "load_reason": "include"})
            self.run_gate("instructions", payload, expected=0)
        generation_file = self.race_state("race-1") / "generation.json"
        first = json.loads(generation_file.read_text(encoding="utf-8"))
        self.assertEqual("instructions", first.get("created_by"))
        init_event = dict(event)
        init_event["source"] = "startup"
        self.run_gate("init", init_event, expected=0)
        second = json.loads(generation_file.read_text(encoding="utf-8"))
        self.assertEqual(first["generation"], second["generation"])  # startup 不旋轉
        pretool_event = dict(event)
        pretool_event.update({"tool_name": "Bash", "tool_input": {"command": "true"}})
        self.assertIsNone(self.output(self.run_gate("pretool", pretool_event, expected=0)))

    def test_resume_rotates_instructions_created_generation(self):
        event = {"session_id": "race-2", "bundle_sha256": self.bundle_hash}
        payload = dict(event)
        payload.update({"file_path": str(self.bundle / "GLOBAL.md"), "load_reason": "include"})
        self.run_gate("instructions", payload, expected=0)
        generation_file = self.race_state("race-2") / "generation.json"
        first = json.loads(generation_file.read_text(encoding="utf-8"))
        init_event = dict(event)
        init_event["source"] = "resume"
        self.run_gate("init", init_event, expected=0)
        second = json.loads(generation_file.read_text(encoding="utf-8"))
        self.assertNotEqual(first["generation"], second["generation"])  # resume 必旋轉
        pretool_event = dict(event)
        pretool_event.update({"tool_name": "Bash", "tool_input": {"command": "true"}})
        self.assert_denied(self.run_gate("pretool", pretool_event, expected=0))  # 舊收據失效


if __name__ == "__main__":
    unittest.main()
