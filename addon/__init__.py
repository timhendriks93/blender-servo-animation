import bpy

from .props.bone_property_group import BonePropertyGroup
from .props.wm_property_group import WindowManagerPropertyGroup
from .ui.bone_panel import BonePanel
from .ui.menu_panel import MenuPanel
from .ops.json_export import JsonExport
from .ops.arduino_export import ArduinoExport
from .ops.binary_export import BinaryExport
from .ops.stop_live_mode import StopLiveMode
from .ops.start_live_mode import StartLiveMode
from .ops.calibrate_servo import CalibrateServo


classes = (
    BonePropertyGroup,
    WindowManagerPropertyGroup,
    BonePanel,
    MenuPanel,
    ArduinoExport,
    JsonExport,
    BinaryExport,
    StopLiveMode,
    StartLiveMode,
    CalibrateServo
)


def menu_func_export(self, _):
    self.layout.operator(ArduinoExport.bl_idname)
    self.layout.operator(JsonExport.bl_idname)
    self.layout.operator(BinaryExport.bl_idname)


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


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Bone.servo_settings
    del bpy.types.EditBone.servo_settings
    del bpy.types.WindowManager.servo_animation
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TIME_MT_editor_menus.remove(menu_func_timeline)
