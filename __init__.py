import operator
import json
import re
import math
import mathutils
import bpy_extras
import bpy

from .src.property_group import ServoAnimationPropertyGroup
from .src.panel import ServoAnimationPanel
from .src.json_export import ServoAnimationJsonExport
from .src.arduino_export import ServoAnimationArduinoExport

bl_info = {
    "name": "Export Animation as Servo Position Values",
    "author": "Tim Hendriks",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Bone Properties > Servo Settings | File > Import-Export",
    "description": "Exports armature animations as servo position values.",
    "warning": "",
    "doc_url": "https://github.com/timhendriks93/blender-servo-animation#readme",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


classes = (
    ServoAnimationPropertyGroup,
    ServoAnimationPanel,
    ServoAnimationArduinoExport,
    ServoAnimationJsonExport
)


def menu_func_export(self, _):
    self.layout.operator(ServoAnimationArduinoExport.bl_idname,
                         text="Animation Servo Positions (.h)")
    self.layout.operator(ServoAnimationJsonExport.bl_idname,
                         text="Animation Servo Positions (.json)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Bone.servo_settings = bpy.props.PointerProperty(
        type=ServoAnimationPropertyGroup)
    bpy.types.EditBone.servo_settings = bpy.props.PointerProperty(
        type=ServoAnimationPropertyGroup)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Bone.servo_settings
    del bpy.types.EditBone.servo_settings
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
