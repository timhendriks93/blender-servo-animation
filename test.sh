#!/bin/sh

blender -noaudio --background examples/Simple/simple.blend --addons servo_animation --python tests/main.py --python-exit-code 1

exit $?
