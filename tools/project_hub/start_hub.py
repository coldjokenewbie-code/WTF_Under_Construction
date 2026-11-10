#!/usr/bin/env python3
"""Installed shared launch entry; configured quota delegation is handled by the CLI."""
from pathlib import Path
import sys
from project_hub.cli import main

if __name__ == "__main__":
    wtf = Path(__file__).resolve().parents[2]
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    main([command, "--settings", str(wtf / "workingfiles/outputs/_shared/project_hub/settings.json"), "--delivery-mode", "enabled"])
