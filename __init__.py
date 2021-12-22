import operator
import json
import re
import mathutils
import math
import bpy_extras
import bpy

from .classes.convert import SERVOANIMATION_converter
from .classes.property_group import SERVOANIMATION_PG_servo_settings
from .classes.panel import SERVOANIMATION_PT_servo_settings
from .classes.json_export import SERVOANIMATION_OT_export_json
from .classes.arduino_export import SERVOANIMATION_OT_export_arduino

bl_info = {
    "name": "Export Animation as Servo Position Values",
    "author": "Tim Hendriks",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Bone Properties > Servo Settings | File > Import-Export",
    "description": "Enables servo settings for bones and exports armature animations as servo position values",
    "warning": "",
    "wiki_url": "https://github.com/timhendriks93/blender-servo-animation#readme",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


classes = (
    SERVOANIMATION_PG_servo_settings,
    SERVOANIMATION_PT_servo_settings,
    SERVOANIMATION_OT_export_arduino,
    SERVOANIMATION_OT_export_json
)


def menu_func_export(self, context):
    self.layout.operator(SERVOANIMATION_OT_export_arduino.bl_idname,
                         text="Animation Servo Positions (.h)")
    self.layout.operator(SERVOANIMATION_OT_export_json.bl_idname,
                         text="Animation Servo Positions (.json)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Bone.servo_settings = bpy.props.PointerProperty(
        type=SERVOANIMATION_PG_servo_settings)
    bpy.types.EditBone.servo_settings = bpy.props.PointerProperty(
        type=SERVOANIMATION_PG_servo_settings)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Bone.servo_settings
    del bpy.types.EditBone.servo_settings
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
