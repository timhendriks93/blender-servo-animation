/*
 * Blender Animation to Servo via PCA9685 Example
 * 
 * This example requires the Adafruit PCA9685 PWM Servo Driver Library:
 * https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library
*/

#define FPS 24
#define FRAMES 100
#define SERVONUM 0

// Exported position arrays (via .h file export option) can be placed here
const int Bone[100] PROGMEM = {375, 375, 376, 378, 380, 382, 385, 389, 393, 397, 401, 406, 411, 416, 421, 426, 431, 437, 442, 447, 452, 457, 461, 466, 470, 474, 477, 480, 483, 485, 486, 487, 488, 487, 485, 482, 478, 474, 468, 461, 454, 446, 438, 429, 420, 410, 400, 390, 380, 370, 360, 350, 340, 330, 321, 312, 304, 296, 289, 282, 276, 272, 268, 265, 263, 262, 263, 264, 265, 267, 269, 272, 275, 278, 282, 286, 290, 295, 299, 304, 309, 314, 319, 324, 329, 333, 338, 343, 347, 352, 356, 359, 363, 366, 368, 371, 373, 374, 375, 375};

const float frameDurationMillis = 1000 / FPS;
const float animationDurationMillis = FRAMES * frameDurationMillis;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
long startMillis = millis();

void setup() {
  pwm.begin();
  pwm.setPWMFreq(60);

  delay(10);
}

void loop() {
  long currentMillis = millis();
  long positionMillis = currentMillis - startMillis;

  if (positionMillis >= animationDurationMillis) {
    startMillis = currentMillis;
  } else {
    long frame = floor(positionMillis / frameDurationMillis);

    // Copy and adjust the following two lines for each additional servo / bone
    int positionValue = pgm_read_word_near(Bone + frame);
    pwm.setPWM(SERVONUM, 0, positionValue);
  }
}
