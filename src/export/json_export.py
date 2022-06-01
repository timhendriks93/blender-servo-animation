import json
import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class JsonExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_positions_json"
    bl_label = "Animation Servo Positions (.json)"
    bl_description = "Save a JSON file with servo position values of the active armature"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )

    def export(self, positions, context):
        fps, frames, seconds = self.get_time_meta(context.scene)
        filename = self.get_filename()

        data = {
            "description": 'Blender Animation Servo Positions',
            "fps": fps,
            "frames": frames,
            "seconds": seconds,
            "bones": len(positions),
            "armature": context.object.name,
            "file": filename,
            "positions": positions
        }

        return json.dumps(data, indent=4)
