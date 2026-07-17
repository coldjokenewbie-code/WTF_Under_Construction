#!/usr/bin/env python3
"""Create immutable, content-addressed WTF session bundles."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
from pathlib import Path

SOURCE_NAMES = ("GLOBAL.md", "AGENTS.md")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_record(path: Path, max_bytes: int | None, max_lines: int | None) -> tuple[bytes, dict]:
    data = path.read_bytes()
    data.decode("utf-8")
    lines = len(data.splitlines())
    if max_bytes is not None and len(data) > max_bytes:
        raise ValueError(f"{path.name} exceeds max_source_bytes={max_bytes}")
    if max_lines is not None and lines > max_lines:
        raise ValueError(f"{path.name} exceeds max_source_lines={max_lines}")
    return data, {"sha256": sha256(data), "bytes": len(data), "lines": lines}


def manifest_bytes(records: dict[str, dict]) -> bytes:
    manifest = {"schema": 1, "sources": records}
    return (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def verify_existing(target: Path, expected_manifest: bytes, sources: dict[str, bytes]) -> None:
    if not target.is_dir() or (target / "manifest.json").read_bytes() != expected_manifest:
        raise FileExistsError(f"immutable bundle collision: {target}")
    for name, data in sources.items():
        if (target / name).read_bytes() != data:
            raise FileExistsError(f"immutable bundle was modified: {target / name}")


def create_bundle(
    global_source: Path,
    agents_source: Path,
    home: Path | None = None,
    max_source_bytes: int | None = None,
    max_source_lines: int | None = None,
) -> Path:
    """Create a bundle without ever rewriting an existing bundle directory."""
    paths = dict(zip(SOURCE_NAMES, (Path(global_source), Path(agents_source))))
    payloads: dict[str, bytes] = {}
    records: dict[str, dict] = {}
    for name, path in paths.items():
        payloads[name], records[name] = file_record(path, max_source_bytes, max_source_lines)
    encoded_manifest = manifest_bytes(records)
    bundle_hash = sha256(encoded_manifest)
    base = (Path(home) if home is not None else Path.home()) / ".claude" / "wtf-session-bundles"
    target = base / bundle_hash
    base.mkdir(parents=True, exist_ok=True)
    if target.exists():
        verify_existing(target, encoded_manifest, payloads)
        return target
    temporary = base / f".{bundle_hash}.{secrets.token_hex(8)}.tmp"
    try:
        temporary.mkdir(mode=0o700)
        for name, data in payloads.items():
            (temporary / name).write_bytes(data)
        (temporary / "manifest.json").write_bytes(encoded_manifest)
        try:
            os.replace(temporary, target)
        except OSError:
            if not target.exists():
                raise
            verify_existing(target, encoded_manifest, payloads)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-source", type=Path, required=True)
    parser.add_argument("--agents-source", type=Path, required=True)
    parser.add_argument("--home", type=Path)
    parser.add_argument("--max-source-bytes", type=int)
    parser.add_argument("--max-source-lines", type=int)
    args = parser.parse_args()
    bundle = create_bundle(args.global_source, args.agents_source, args.home,
                           args.max_source_bytes, args.max_source_lines)
    print(bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
