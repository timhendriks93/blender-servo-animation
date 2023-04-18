#!/bin/bash

blender \
    -noaudio \
    --background examples/Simple/simple.blend \
    --addons servo_animation \
    --python tests/main.py

exit $?
