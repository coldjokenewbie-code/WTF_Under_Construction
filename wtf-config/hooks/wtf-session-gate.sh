#!/bin/sh
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT_DIR/wtf-session-gate.py" "$@"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$SCRIPT_DIR/wtf-session-gate.py" "$@"
fi
echo "wtf-session-gate: python3 and python are unavailable; denying hook" >&2
exit 2
