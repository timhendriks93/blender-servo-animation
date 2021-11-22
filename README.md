# Blender Servo Animation Add-on

Export your Blender animation to servo position values. They can be used with an Arduino compatible micro controller to move PWM-driven servos according to your animation.

Animate your robot or animatronic project and take advantage of Blender's animation tools!

## Installation

Note that this Add-on is compatible with Blender version 2.80 or higher.

1. Download the `blender_servo_animation_addon.py` file.
2. Open Blender and go to `File > Preferences > Add-ons`.
3. Click the `Install...` button, select the previously downloaded file and click `Install Add-on`.
4. Enable the Add-on by enabling the checkbox in the Add-ons list.

## Usage

### Providing Servo Settings

After enabling this Add-on, you should be able to define servo settings for each bone of an armature. The underlying principle is that each bone represents a servo motor in a real world build.

Make sure to select a specific bone within the armature while in Edit or Pose mode. You should now see a panel showing the current servo settings for the selected bone.

![Servo Settings panel](screenshots/servo_settings.png)

| Property               | Description                                                                                                                                                                                           |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Provide Servo Settings | Define servo settings for this bone and include its position values when exporting                                                                                                                    |
| Position Min           | The minimum position value before the servo physically stops moving                                                                                                                                   |
| Position Max           | Same as `Position Min`, but for the maximum value                                                                                                                                                     |
| Set Position Limits    | Define a position range to limit the calculated position values according to a specific build                                                                                                         |
| Position Limit Start   | The minimum position value before the servo is supposed to stop moving within a specific build                                                                                                        |
| Position Limit End     | Same as `Position Limit Start`, but for the end value                                                                                                                                                 |
| Neutral Angle          | The assumed neutral angle of the servo in degrees (typically half the rotation range) which should be adjusted carefully, since the servo will first move to its 'natural' neutral angle when powered |
| Rotation Range         | The manufactured rotation range of the servo in degrees (typically 180)                                                                                                                               |
| Euler Rotation Axis    | The Euler rotation axis (X, Y or Z) of the bone rotation representing the servo movement                                                                                                              |
| Multiplier             | Multilplier to increase or decrease the rotation to adjust the intensity within a specific build                                                                                                      |
| Reverse Direction      | Whether the applied rotation should be reversed when converting to position value which might be necessary to reflect the servo's positioning within a specific build                                 |

Note that the correct settings vary between different servo brands and models. Be careful not to damage the servo when finding the min and max position values. The range of motion of a servo can be limited depending on your specific build design. In this case you can use the position limit values to avoid damage to your build.

### Choosing a position value range

The default position min and max values are based on servo pulse lengths as they are required when using a library to control a servo driver module, like the PCA9685. It is also possible to use a different kind of value range. For example, to use the default Arduino Servo library, you can use a degrees value range by setting min to `0` and max to `180`.

### Animating the armature

When animating your armature you can benefit from all the exciting animation features Blender has to offer. Apart from animating every bone/servo separately, you can also use IK ([Inverse Kinematics](https://www.youtube.com/watch?v=S-2v_CKmVE8)) to let the Add-On calculate the positions of multiple servos automatically.

When thinking of animatronic or robotic projects, you could animate a head or arm without having to worry about the individual bones/servos that make up the neck mechanism or arm segments. To further illustrate this, you can also find an [example of a neck mechanism](examples/IK/ik.blend) to learn about the armature and constraints setup.

### Exporting

Once all servo settings are provided and the animation is completed, you can calculate and export the servo position values. There are two different formats to choose from:

1. `Animation Servo Positions (.h)`: An Arduino/C/C++ style header file which can be easily included in an Arduino project.
2. `Animation Servo Positions (.json)`: A simple (non-formatted) JSON file which can be used in a more generic way.

Make sure to select the armature containing the bones/servos you want to export and select the desired format in the `File > Export` menu:

![Servo Settings panel](screenshots/export_menu.png)

## Using the exported data

This repository contains some [examples](examples) about how to use the exported data with micro controllers. You'll find some Arduino project examples with a very basic program to play back the exported animation.

Of course you can also implement a more sophisticated solution, e.g. by adding a start and stop logic, choosing from multiple animations or handling multiple servos in a more efficient way. Since you'll most likely want to animate more than one servo, you can also find a basic example on how to [control multiple servos using a PCA9685 PWM module](examples/ArduinoPCA9685/ArduinoPCA9685.ino).