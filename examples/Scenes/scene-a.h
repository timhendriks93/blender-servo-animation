/*
  Blender Servo Animation Positions

  FPS: 30
  Frames: 100
  Seconds: 3
  Bones: 1
  Armature: Armature
  Scene: SceneA
  File: scenes.blend
*/

#include <Arduino.h>

namespace SceneA {

const byte FPS = 30;
const int FRAMES = 100;
const int LENGTH = 600;

const byte PROGMEM ANIMATION_DATA[LENGTH] = {
    0x3c, 0x00, 0x05, 0xc0, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xc1, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0xc5, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xcb, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0xd4, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xde, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0xeb, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xf9, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0x08, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0x1a, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0x2c, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0x3f, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0x53, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0x68, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0x7d, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0x92, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0xa8, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0xbe, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0xd3, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0xe8, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0xfd, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x11, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x24, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x36, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x48, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x57, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x65, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x72, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x7c, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x85, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x8b, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x8f, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x90, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x8e, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x86, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x7a, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x6a, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x57, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x3f, 0x3e, 0x0a, 0x3c, 0x00, 0x07, 0x24, 0x3e, 0x0a,
    0x3c, 0x00, 0x07, 0x07, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0xe7, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0xc4, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0x9f, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0x79, 0x3e, 0x0a, 0x3c, 0x00, 0x06, 0x51, 0x3e, 0x0a,
    0x3c, 0x00, 0x06, 0x29, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xff, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0xd5, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xab, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0x81, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0x57, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0x2f, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0x07, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0xe1, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0xbc, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x99, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x79, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x5c, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x41, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x29, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x16, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x06, 0x3e, 0x0a, 0x3c, 0x00, 0x03, 0xfa, 0x3e, 0x0a,
    0x3c, 0x00, 0x03, 0xf2, 0x3e, 0x0a, 0x3c, 0x00, 0x03, 0xf0, 0x3e, 0x0a,
    0x3c, 0x00, 0x03, 0xf1, 0x3e, 0x0a, 0x3c, 0x00, 0x03, 0xf5, 0x3e, 0x0a,
    0x3c, 0x00, 0x03, 0xfa, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x02, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x0b, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x16, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x23, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x31, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x40, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x51, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x62, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x75, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0x88, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0x9b, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0xaf, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0xc4, 0x3e, 0x0a,
    0x3c, 0x00, 0x04, 0xd8, 0x3e, 0x0a, 0x3c, 0x00, 0x04, 0xec, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0x01, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0x15, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0x28, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0x3b, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0x4e, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0x5f, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0x70, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0x7f, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0x8d, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0x9a, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0xa5, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xae, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0xb6, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xbb, 0x3e, 0x0a,
    0x3c, 0x00, 0x05, 0xbf, 0x3e, 0x0a, 0x3c, 0x00, 0x05, 0xc0, 0x3e, 0x0a,
};

} // namespace SceneA
