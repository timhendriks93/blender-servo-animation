#!/bin/bash

TESTSDIR=$(dirname "$0")

blender \
    -noaudio \
    --background $TESTSDIR/../examples/Simple/simple.blend \
    --addons servo_animation \
    --python-use-system-env \
    --python-exit-code 1 \
    --python $TESTSDIR/test.py

exit $?
