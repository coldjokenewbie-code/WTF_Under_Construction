#!/usr/bin/env python3
"""Own-process lifecycle only. Never pkill; never start a quota watcher here."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "project_hub"
from .errors import HubError
from .paths import no_symlinks
from .storage import atomic_json, locked, read_json


def process_token(pid):
    result = subprocess.run(["ps", "-p", str(pid), "-o", "lstart=", "-o", "command="], capture_output=True, text=True, timeout=5)
    return result.stdout.strip() if result.returncode == 0 else ""


def health(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=2) as response:
            return json.load(response)
    except (OSError, ValueError, urllib.error.URLError):
        return {}


def port_busy(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def verify_owned(record, settings):
    if record.get("settings") != str(settings) or not isinstance(record.get("pid"), int):
        return False
    current = process_token(record["pid"])
    return bool(current) and current == record.get("process_token") and str(Path(__file__).with_name("server.py")) in current


def start(settings, runtime, port, mode):
    record_path = runtime / "process.json"
    with locked(runtime):
        record = read_json(record_path, {})
        if verify_owned(record, settings):
            status = health(port)
            if record.get("port") != port or record.get("delivery_mode") != mode or status.get("settings") != str(settings) or status.get("delivery_mode") != mode:
                raise HubError("running_configuration_mismatch", "既有服務port／mode／settings不同，請明確停止後重啟", 409)
            ensure_quota(settings, mode)
            return dict(ok=True, message="既有共用指揮中心已在執行", **record)
        if port_busy(port):
            raise HubError("port_in_use", "此連接埠已有服務，不接管也不停用", 409)
        ensure_quota(settings, mode)
        command = [sys.executable, str(Path(__file__).with_name("server.py")), "--settings", str(settings),
                   "--port", str(port), "--delivery-mode", mode]
        with no_symlinks(runtime / "server.log").open("a") as log:
            child = subprocess.Popen(command, start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
        token = process_token(child.pid)
        record = dict(pid=child.pid, process_token=token, settings=str(settings), port=port, delivery_mode=mode)
        atomic_json(record_path, record)
    for _attempt in range(20):
        status = health(port)
        if status.get("pid") == child.pid and status.get("service") == "project_hub" and status.get("settings") == str(settings) and status.get("delivery_mode") == mode:
            record["process_token"] = process_token(child.pid)
            with locked(runtime):
                atomic_json(record_path, record)
            return dict(ok=True, **record)
        if child.poll() is not None:
            break
        time.sleep(.25)
    raise HubError("start_failed", "候選服務未通過啟動檢查，請查看server.log", 500)


def ensure_quota(settings, mode):
    command = read_json(settings, {}).get("quota_delegate_command")
    if mode == "enabled" and command:
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            raise HubError("invalid_quota_delegate", "額度委託命令格式無效")
        subprocess.run(command, check=True, timeout=30)


def stop(settings, runtime):
    with locked(runtime):
        record = read_json(runtime / "process.json", {})
        if not verify_owned(record, settings):
            raise HubError("not_owned", "無法證實此PID是本設定啟動的服務；拒絕停止", 409)
        os.kill(record["pid"], signal.SIGTERM)
        return {"ok": True, "stopped_pid": record["pid"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "stop", "restart", "status"))
    parser.add_argument("--settings", required=True)
    parser.add_argument("--port", type=int, default=8780)
    parser.add_argument("--delivery-mode", choices=("disabled", "enabled"), default="disabled")
    args = parser.parse_args(argv)
    settings = no_symlinks(args.settings).resolve()
    config = read_json(settings, {})
    runtime = no_symlinks(config.get("runtime_dir", str(settings.parent / "runtime")))
    if args.command == "status":
        result = {"process": read_json(runtime / "process.json", {}), "health": health(args.port)}
    else:
        if args.command in ("stop", "restart"):
            result = stop(settings, runtime)
            if args.command == "restart":
                time.sleep(.5)
        if args.command in ("start", "restart"):
            result = start(settings, runtime, args.port, args.delivery_mode)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except HubError as error:
        print(json.dumps(error.payload(), ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
