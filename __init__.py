import operator
import json
import re
import math
import mathutils
import bpy_extras
import bpy
import serial

from bpy.app.handlers import persistent

from .src.bone_property_group import ServoAnimationBonePropertyGroup
from .src.wm_property_group import ServoAnimationWindowManagerPropertyGroup
from .src.panel import ServoAnimationPanel
from .src.json_export import ServoAnimationJsonExport
from .src.arduino_export import ServoAnimationArduinoExport
from .src.converter import ServoAnimationConverter
from .src.timeline_menu import ServoAnimationTimelineMenu
from .src.live import live_controller

bl_info = {
    "name": "Export Animation as Servo Position Values",
    "author": "Tim Hendriks",
    "version": (1, 2, 0),
    "blender": (2, 80, 0),
    "location": "Bone Properties > Servo Settings | File > Import-Export",
    "description": "Exports armature animations as servo position values.",
    "warning": "",
    "doc_url": "https://github.com/timhendriks93/blender-servo-animation#readme",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


classes = (
    ServoAnimationBonePropertyGroup,
    ServoAnimationWindowManagerPropertyGroup,
    ServoAnimationPanel,
    ServoAnimationArduinoExport,
    ServoAnimationJsonExport,
    ServoAnimationTimelineMenu
)


@persistent
def on_frame_change_pre(scene):
    live_controller.on_frame_change_pre(scene)


@persistent
def on_frame_change_post(scene):
    live_controller.on_frame_change_post(scene)


def menu_func_export(self, _):
    self.layout.operator(ServoAnimationArduinoExport.bl_idname)
    self.layout.operator(ServoAnimationJsonExport.bl_idname)


def menu_func_timeline(self, _):
    self.layout.menu(ServoAnimationTimelineMenu.bl_idname)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Bone.servo_settings = bpy.props.PointerProperty(
        type=ServoAnimationBonePropertyGroup)
    bpy.types.EditBone.servo_settings = bpy.props.PointerProperty(
        type=ServoAnimationBonePropertyGroup)
    bpy.types.WindowManager.servo_animation = bpy.props.PointerProperty(
        type=ServoAnimationWindowManagerPropertyGroup)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TIME_MT_editor_menus.append(menu_func_timeline)
    bpy.app.handlers.frame_change_pre.append(on_frame_change_pre)
    bpy.app.handlers.frame_change_post.append(on_frame_change_post)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Bone.servo_settings
    del bpy.types.EditBone.servo_settings
    del bpy.types.WindowManager.servo_animation
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TIME_MT_editor_menus.remove(menu_func_timeline)
    bpy.app.handlers.frame_change_pre.remove(on_frame_change_pre)
    bpy.app.handlers.frame_change_post.remove(on_frame_change_post)
