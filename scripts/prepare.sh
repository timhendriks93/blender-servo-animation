#!/bin/bash

PARENTDIR=$(dirname "$current_dir")
TESTSDIR="$PARENTDIR/tests"

blender \
    -noaudio \
    --background \
    --python-use-system-env \
    --python-exit-code 1 \
    --python $TESTSDIR/prepare.py

exit $?
