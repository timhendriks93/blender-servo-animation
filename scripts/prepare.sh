#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TESTSDIR="$ROOT_DIR/tests"

blender \
    -noaudio \
    --background \
    --python-use-system-env \
    --python-exit-code 1 \
    --python "$TESTSDIR/prepare.py"

exit $?
