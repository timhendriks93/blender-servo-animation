#!/bin/bash

TESTSDIR=$(dirname "$0")

blender \
    -noaudio \
    --background \
    --python-use-system-env \
    --python-exit-code 1 \
    --python $TESTSDIR/prepare.py

exit $?
