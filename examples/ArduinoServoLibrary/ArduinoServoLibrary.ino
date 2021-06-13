/*
 * Blender Animation to Servo Example
*/

#include <Servo.h>

#define FPS 24
#define FRAMES 100
#define PWM_PIN 9

const float Bone[100] PROGMEM = {90.0, 89.87, 89.49, 88.89, 88.07, 87.05, 85.85, 84.48, 82.97, 81.32, 79.56, 77.7, 75.76, 73.75, 71.7, 69.61, 67.5, 65.39, 63.3, 61.25, 59.24, 57.3, 55.44, 53.68, 52.03, 50.52, 49.15, 47.95, 46.93, 46.11, 45.51, 45.13, 45.0, 45.24, 45.95, 47.1, 48.65, 50.57, 52.84, 55.43, 58.3, 61.43, 64.78, 68.33, 72.05, 75.9, 79.85, 83.88, 87.96, 92.04, 96.12, 100.15, 104.1, 107.95, 111.67, 115.22, 118.57, 121.7, 124.57, 127.16, 129.43, 131.35, 132.9, 134.05, 134.76, 135.0, 134.89, 134.55, 134.01, 133.28, 132.37, 131.29, 130.06, 128.7, 127.21, 125.61, 123.92, 122.14, 120.29, 118.39, 116.45, 114.48, 112.5, 110.52, 108.55, 106.61, 104.71, 102.86, 101.08, 99.39, 97.79, 96.3, 94.94, 93.71, 92.63, 91.72, 90.99, 90.45, 90.11, 90.0};
//const int Bone[100] PROGMEM = {90, 89, 89, 88, 88, 87, 85, 84, 82, 81, 79, 77, 75, 73, 71, 69, 67, 65, 63, 61, 59, 57, 55, 53, 52, 50, 49, 47, 46, 46, 45, 45, 45, 45, 45, 47, 48, 50, 52, 55, 58, 61, 64, 68, 72, 75, 79, 83, 87, 92, 96, 100, 104, 107, 111, 115, 118, 121, 124, 127, 129, 131, 132, 134, 134, 135, 134, 134, 134, 133, 132, 131, 130, 128, 127, 125, 123, 122, 120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 101, 99, 97, 96, 94, 93, 92, 91, 90, 90, 90, 90};
const float frameDurationMillis = 1000 / FPS;
const float animationDurationMillis = FRAMES * frameDurationMillis;

Servo myservo;
long startMillis = millis();

void setup() {
  myservo.attach(PWM_PIN);
}

void loop() {
  long currentMillis = millis();
  long positionMillis = currentMillis - startMillis;

  if (positionMillis >= animationDurationMillis) {
    startMillis = currentMillis;
  } else {
    long frame = floor(positionMillis / frameDurationMillis);
    float positionValue = pgm_read_float_near(Bone + frame);
    //int positionValue = pgm_read_word_near(Bone + frame);

    myservo.write(positionValue);
  }
}
