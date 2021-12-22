import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .converter import SERVOANIMATION_converter


class SERVOANIMATION_OT_export_json(Operator, ExportHelper):
    bl_idname = "export_anim.servo_positions_json"
    bl_label = "Export Animation Servo Positions (.json)"
    bl_description = "Save a JSON file with servo position values from an armature"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )
    precision: bpy.props.IntProperty(
        name="Precision",
        description="The number of decimal digits to round to",
        default=0,
        min=0,
        max=6
    )

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'ARMATURE'

    def execute(self, context):
        scene = context.scene
        original_frame = scene.frame_current

        try:
            converter = SERVOANIMATION_converter()
            positions = converter.calculate_positions(context, self.precision)
            data = {
                "description": 'Blender Animation Servo Positions',
                "fps": scene.render.fps,
                "frames": scene.frame_end - scene.frame_start + 1,
                "armature": context.object.name,
                "positions": positions
            }
            content = json.dumps(data, indent=4)
        except RuntimeError as error:
            scene.frame_set(original_frame)
            self.report({'ERROR'}, str(error))

            return {'CANCELLED'}

        scene.frame_set(original_frame)

        f = open(self.filepath, 'w', encoding='utf-8')
        f.write(content)
        f.close()

        return {'FINISHED'}
