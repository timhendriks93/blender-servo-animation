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

import bpy
import bpy_extras
import math
import mathutils
import re
import json
import operator


class SERVOANIMATION_converter:
    positions = {}
    neutrals = {}
    
    def range_map(self, value, fromLow, fromHigh, toLow, toHigh):
        return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow
    
    def matrix_visual(self, pose_bone):
        bone = pose_bone.bone

        matrix_pose_bone = pose_bone.matrix
        matrix_bone = bone.matrix_local

        if bone.parent:
            matrix_parent_bone = bone.parent.matrix_local.copy()
            matrix_parent_pose_bone = pose_bone.parent.matrix.copy()
        else:
            matrix_parent_bone = mathutils.Matrix()
            matrix_parent_pose_bone = mathutils.Matrix()

        matrix_bone_inverted = matrix_bone.copy().inverted()
        matrix_parent_pose_bone_inverted = matrix_parent_pose_bone.copy().inverted()

        return matrix_bone_inverted @ matrix_parent_bone @ matrix_parent_pose_bone_inverted @ matrix_pose_bone
            
    def calculate_positions_for_frame(self, frame, pose_bones, scene, precision):
        scene.frame_set(frame)
            
        for pose_bone in pose_bones:
            bone = pose_bone.bone
            servo_settings = bone.servo_settings
            rotation_euler = self.matrix_visual(pose_bone).to_euler()
            rotation_axis_index = int(servo_settings.rotation_axis)
            rotation_in_degrees = round(math.degrees(rotation_euler[rotation_axis_index]) * servo_settings.multiplier, 2)
            
            if frame == 1:
                self.neutrals[bone.name] = rotation_in_degrees

            rotation_diff = rotation_in_degrees - self.neutrals[bone.name]
            
            if servo_settings.reverse_direction == True:
                rotation_diff = rotation_diff * -1
            
            angle = servo_settings.neutral_angle - rotation_diff
            position = round(self.range_map(angle, 0, servo_settings.rotation_range, servo_settings.position_min, servo_settings.position_max), precision)
            
            check_min = servo_settings.position_min
            check_max = servo_settings.position_max
            
            if servo_settings.set_position_limits == True:
                check_min = servo_settings.position_limit_start
                check_max = servo_settings.position_limit_end
            
            if position < check_min or position > check_max:
                raise RuntimeError('Calculated position ' + str(position) + ' for bone ' + bone.name + ' is out of range (' + str(check_min) + ' - ' + str(check_max) + ') at frame ' + str(frame) + '.')
            
            self.positions[bone.name].append(str(position))
            
    def calculate_positions(self, context, precision):
        pose_bones = []
        scene = context.scene
        
        self.positions = {}
        self.neutrals = {}
        
        for pose_bone in context.object.pose.bones:
            if pose_bone.bone.servo_settings.active == True:
                pose_bones.append(pose_bone)
                self.positions[pose_bone.bone.name] = []
        
        if precision == 0:
            precision = None
        
        for frame in range(scene.frame_start, scene.frame_end + 1):
            self.calculate_positions_for_frame(frame, pose_bones, scene, precision)
            
        return self.positions


class SERVOANIMATION_OT_export_arduino(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "export_anim.servo_positions_arduino"
    bl_label = "Export Animation Servo Positions (.h)"
    bl_description = "Save an Arduino header file with servo position values from an armature"
    
    filename_ext = ".h"
    
    filter_glob: bpy.props.StringProperty(
        default="*.h",
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
    use_progmem: bpy.props.BoolProperty(
        name="Add PROGMEM modifier",
        description="Add the PROGMEM modifier to each position array which enables an Arduino micro controller to handle large arrays",
        default=True
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
            frame_count = scene.frame_end - scene.frame_start + 1;
            variable_type = 'int' if self.precision == 0 else 'float'
            content = '/*\n  Servo Position value Animation\n\n  FPS: ' + str(scene.render.fps) + '\n  Frames: ' + str(frame_count) + '\n  Armature: ' + str(context.object.name) + '\n*/\n\n'
            
            for bone_name in positions:
                variable_name = re.sub('[^a-zA-Z0-9_]', '', bone_name)
                content = content + 'const ' + variable_type + ' ' + variable_name + '[' + str(frame_count) + '] '
                
                if self.use_progmem == True:
                    content = content + 'PROGMEM '
                    
                content = content + '= {' + ', '.join(positions[bone_name]) + '};\n'
            
            content = content + '\n'
        except RuntimeError as error:
            scene.frame_set(original_frame)
            self.report({'ERROR'}, str(error))
            
            return {'CANCELLED'}
            
        scene.frame_set(original_frame)
        
        f = open(self.filepath, 'w', encoding='utf-8')
        f.write(content)
        f.close()
            
        return {'FINISHED'}
    
    
class SERVOANIMATION_OT_export_json(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
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
                "description": 'Servo Position value Animation',
                "fps": scene.render.fps,
                "frames": scene.frame_end - scene.frame_start + 1,
                "armature": context.object.name,
                "positions": positions
            }
            content = json.dumps(data)
        except RuntimeError as error:
            scene.frame_set(original_frame)
            self.report({'ERROR'}, str(error))
            
            return {'CANCELLED'}
            
        scene.frame_set(original_frame)
        
        f = open(self.filepath, 'w', encoding='utf-8')
        f.write(content)
        f.close()
            
        return {'FINISHED'}


class SERVOANIMATION_PG_servo_settings(bpy.types.PropertyGroup):
    def range_limit_value(self, value, min_value, max_value):
        if min_value is not None and value < min_value:
            return min_value
        elif max_value is not None and value > max_value:
            return max_value
        else:
            return value
        
    def update_position_min(self, context):
        self["position_min"] = self.range_limit_value(self.position_min, None, self.position_max)
            
    def update_position_max(self, context):
        self["position_max"] = self.range_limit_value(self.position_max, self.position_min, None)
            
    def update_position_limit_start(self, context):
        self["position_limit_start"] = self.range_limit_value(self.position_limit_start, self.position_min, self.position_limit_end)
            
    def update_position_limit_end(self, context):
        self["position_limit_end"] = self.range_limit_value(self.position_limit_end, self.position_limit_start, self.position_max)
            
    def update_neutral_angle(self, context):
        self["neutral_angle"] = self.range_limit_value(self.neutral_angle, None, self.rotation_range)
    
    active: bpy.props.BoolProperty(
        name="Provide Servo Settings",
        description="Provide servo settings for this bone"
    )
    position_min: bpy.props.IntProperty(
        name="Min Position",
        default=150,
        min=0,
        max=10000,
        description="The minimum position value before the servo physically stops moving",
        update=update_position_min
    )
    position_max: bpy.props.IntProperty(
        name="Max Position",
        default=600,
        min=0,
        max=10000,
        description="The maximum position value before the servo physically stops moving"
    )
    position_limit_start: bpy.props.IntProperty(
        name="Position Limit Start",
        default=150,
        min=0,
        max=10000,
        description="The minimum position value before the servo is supposed to stop moving within a specific build"
    )
    position_limit_end: bpy.props.IntProperty(
        name="Position Limit End",
        default=600,
        min=0,
        max=10000,
        description="The maximum position value before the servo is supposed to stop moving within a specific build"
    )
    neutral_angle: bpy.props.IntProperty(
        name="Neutral Angle",
        default=90,
        min=0,
        max=360,
        description="The assumed neutral angle of the servo in degrees (typically half the rotation range) which should be adjusted carefully, since the servo will first move to its 'natural' neutral angle when powered"
    )
    reverse_direction: bpy.props.BoolProperty(
        name="Reverse Direction",
        description="Whether the applied rotation should be reversed when converting to position value which might be necessary to reflect the servo's positioning within a specific build"
    )
    set_position_limits: bpy.props.BoolProperty(
        name="Set Position Limits",
        description="Define a position range to limit the calculated position values according to a specific build"
    )
    multiplier: bpy.props.FloatProperty(
        name="Multiplier",
        default=1,
        min=0.1,
        max=100,
        precision=1,
        step=10,
        description="Multilplier to increase or decrease the rotation to adjust the intensity within a specific build"
    )
    rotation_range: bpy.props.IntProperty(
        name="Rotation Range",
        default=180,
        min=0,
        max=360,
        description="The manufactured rotation range of the servo in degrees (typically 180)"
    )
    rotation_axis: bpy.props.EnumProperty(
        name="Euler Rotation Axis",
        default=0,
        items=[
            ('0', 'X', "X Euler rotation axis"),
            ('1', 'Y', "Y Euler rotation axis"),
            ('2', 'Z', "Z Euler rotation axis")
        ]
    )


class SERVOANIMATION_PT_servo_settings(bpy.types.Panel):
    bl_label = "Servo Settings"
    bl_idname = "BONE_PT_servo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        return (context.active_bone is not None)

    def draw(self, context):
        layout = self.layout
        servo_settings = context.active_bone.servo_settings
        
        split = layout.split()
        col = split.column()
        col = split.column(align=True)
        col.prop(servo_settings, "active")
        
        if servo_settings.active == True:
            split = layout.split()
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text="Position Min")
            col.label(text="Max")
            col = split.column(align=True)
            col.prop(servo_settings, "position_min", text="")
            col.prop(servo_settings, "position_max", text="")
            col.prop(servo_settings, "set_position_limits")
            
            if servo_settings.set_position_limits == True:
                split = layout.split()
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text="Limit Start")
                col.label(text="End")
                col = split.column(align=True)
                col.prop(servo_settings, "position_limit_start", text="")
                col.prop(servo_settings, "position_limit_end", text="")
            
            split = layout.split()
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text="Neutral Angle")
            col.label(text="Rotation Range")
            col = split.column(align=True)
            col.prop(servo_settings, "neutral_angle", text="")
            col.prop(servo_settings, "rotation_range", text="")
            
            split = layout.split()
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text="Rotation Axis")
            col.label(text="Multiplier")
            col = split.column(align=True)
            col.prop(servo_settings, "rotation_axis", text="")
            col.prop(servo_settings, "multiplier", text="")
            col.prop(servo_settings, "reverse_direction")


classes = (
    SERVOANIMATION_PG_servo_settings,
    SERVOANIMATION_PT_servo_settings,
    SERVOANIMATION_OT_export_arduino,
    SERVOANIMATION_OT_export_json
)


def menu_func_export(self, context):
    self.layout.operator(SERVOANIMATION_OT_export_arduino.bl_idname, text="Animation Servo Positions (.h)")
    self.layout.operator(SERVOANIMATION_OT_export_json.bl_idname, text="Animation Servo Positions (.json)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Bone.servo_settings = bpy.props.PointerProperty(type=SERVOANIMATION_PG_servo_settings)
    bpy.types.EditBone.servo_settings = bpy.props.PointerProperty(type=SERVOANIMATION_PG_servo_settings)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Bone.servo_settings
    del bpy.types.EditBone.servo_settings
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    

if __name__ == "__main__":
    register()
