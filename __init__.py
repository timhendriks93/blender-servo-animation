import bpy

from bpy.app.handlers import persistent

from .src.props.bone_property_group import BonePropertyGroup
from .src.props.wm_property_group import WindowManagerPropertyGroup
from .src.ui.bone_panel import BonePanel
from .src.ui.menu_panel import MenuPanel
from .src.export.json_export import JsonExport
from .src.export.arduino_export import ArduinoExport
from .src.utils.uart import UART_CONTROLLER

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
    BonePropertyGroup,
    WindowManagerPropertyGroup,
    BonePanel,
    MenuPanel,
    ArduinoExport,
    JsonExport
)


@persistent
def on_frame_change_post(scene):
    if bpy.context.screen.is_animation_playing:
        UART_CONTROLLER.update_positions(scene)


def menu_func_export(self, _):
    self.layout.operator(ArduinoExport.bl_idname)
    self.layout.operator(JsonExport.bl_idname)


def menu_func_timeline(self, _):
    self.layout.popover(MenuPanel.bl_idname)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Bone.servo_settings = bpy.props.PointerProperty(
        type=BonePropertyGroup)
    bpy.types.EditBone.servo_settings = bpy.props.PointerProperty(
        type=BonePropertyGroup)
    bpy.types.WindowManager.servo_animation = bpy.props.PointerProperty(
        type=WindowManagerPropertyGroup)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TIME_MT_editor_menus.append(menu_func_timeline)
    bpy.app.handlers.frame_change_post.append(on_frame_change_post)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Bone.servo_settings
    del bpy.types.EditBone.servo_settings
    del bpy.types.WindowManager.servo_animation
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TIME_MT_editor_menus.remove(menu_func_timeline)
    bpy.app.handlers.frame_change_post.remove(on_frame_change_post)
