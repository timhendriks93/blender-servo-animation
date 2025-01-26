#!/bin/bash

PARENTDIR=$(dirname "$current_dir")

blender \
    -noaudio \
    --background \
    --python-use-system-env \
    --python-exit-code 1 \
    --python $PARENTDIR/tests/prepare.py

exit $?
