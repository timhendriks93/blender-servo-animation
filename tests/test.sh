#!/bin/bash

TESTSDIR=$(dirname "$0")

blender \
    -noaudio \
    --background $TESTSDIR/integration/test.blend \
    --addons servo_animation \
    --python-use-system-env \
    --python-exit-code 1 \
    --python $TESTSDIR/test.py \
    > /dev/null 2>&1

cat $TESTSDIR/results.txt

exit $?
