import json
import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class JsonExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_positions_json"
    bl_label = "Export Animation Servo Positions (.json)"
    bl_description = "Save a JSON file with servo position values from an armature"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )

    def export(self, fps, frames, seconds, bones, positions, armature, filename):
        data = {
            "description": 'Blender Animation Servo Positions',
            "fps": fps,
            "frames": frames,
            "seconds": seconds,
            "bones": bones,
            "armature": armature,
            "file": filename,
            "positions": positions
        }

        return json.dumps(data, indent=4)
