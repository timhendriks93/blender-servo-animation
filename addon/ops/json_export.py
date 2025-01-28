import json
import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class JsonExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_animation_json"
    bl_label = "Servo Animation (.json)"
    bl_description = "Save a JSON file with servo position values of the active armature"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )

    indent: bpy.props.EnumProperty(
        name="Indent",
        items=[
            ('None', 'No indent', ''),
            ('1', '1 Space', ''),
            ('2', '2 Spaces', ''),
            ('3', '3 Spaces', ''),
            ('4', '4 Spaces', ''),
        ],
        default='2',
    )

    def export(self, positions, filepath, context):
        fps, frames, seconds = self.get_time_meta(context.scene)
        filename = self.get_blend_filename()

        try:
            indent = int(self.indent)
        except ValueError:
            indent = None

        data = {
            "description": 'Blender Servo Animation Positions',
            "fps": fps,
            "frames": frames,
            "seconds": seconds,
            "bones": len(positions[0]),
            "armature": context.object.name,
            "file": filename,
            "scene": context.scene.name,
            "positions": positions
        }

        content = json.dumps(data, indent=indent)

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
