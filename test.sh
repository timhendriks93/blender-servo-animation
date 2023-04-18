#!/bin/bash

blender \
    -noaudio \
    --background examples/Simple/simple.blend \
    --addons servo_animation \
    --python-use-system-env \
    --python-exit-code 1 \
    --python tests/main.py

exit $?
