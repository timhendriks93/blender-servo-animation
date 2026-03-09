from bpy.types import Menu
from ..ops.json_export import JsonExport
from ..ops.arduino_export import ArduinoExport
from ..ops.binary_export import BinaryExport
from ..ops.text_export import TextExport


class ExportMenu(Menu):
    bl_label = "Export Options"
    bl_idname = "TIMELINE_MT_servo_export"

    def draw(self, _context):
        layout = self.layout
        layout.operator(ArduinoExport.bl_idname, text="Arduino (.h)")
        layout.operator(JsonExport.bl_idname, text="JSON (.json)")
        layout.operator(BinaryExport.bl_idname, text="Binary (.bin)")
        layout.operator(TextExport.bl_idname, text="Text (.txt)")
