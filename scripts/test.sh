#!/bin/bash

PARENTDIR=$(dirname "$current_dir")
TESTSDIR="$PARENTDIR/tests"
TESTFILE="$TESTSDIR/results.txt"

blender \
    -noaudio \
    --background $TESTSDIR/integration/test.blend \
    --addons servo_animation \
    --python-use-system-env \
    --python-exit-code 1 \
    --python $TESTSDIR/test.py \
    > /dev/null 2>&1

cat $TESTFILE

last_line=$(tail -n 1 "$TESTFILE")

if [ "$last_line" == "OK" ]; then
    exit 0
else
    exit 1
fi
