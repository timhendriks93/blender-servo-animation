import bpy

from bpy.types import PropertyGroup
from ..utils.servo_settings import range_limit_value


def update_position_min(self, _context):
    self.position_min = range_limit_value(
        self.position_min, None, self.position_max)


def update_position_max(self, _context):
    self.position_max = range_limit_value(
        self.position_max, self.position_min, None)


def update_neutral_angle(self, _context):
    self.neutral_angle = range_limit_value(
        self.neutral_angle, None, self.rotation_range)


class BonePropertyGroup(PropertyGroup):
    active: bpy.props.BoolProperty(
        name="Provide Servo Settings",
        description="Provide servo settings for this bone"
    )
    servo_id: bpy.props.IntProperty(
        name="Servo ID",
        default=0,
        min=0,
        max=255,
        description="The unique servo ID which is also used for sending live commands"
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
        description="The maximum position value before the servo physically stops moving",
        update=update_position_max
    )
    threshold: bpy.props.IntProperty(
        name="Threshold",
        default=20,
        min=0,
        max=10000,
        description=(
            "The maximum value change between frames which is also "
            "used for frame jump handling in live mode"
        )
    )
    neutral_angle: bpy.props.IntProperty(
        name="Neutral Angle",
        default=90,
        min=0,
        max=360,
        description=(
            "The neutral angle of the servo in degrees (typically half the rotation range) "
            "which resembles the bone's position in the first frame"
        ),
        update=update_neutral_angle
    )
    reverse_direction: bpy.props.BoolProperty(
        name="Reverse Direction",
        description=(
            "Whether the applied rotation should be reversed when converting to "
            "position value which might be necessary to reflect the servo's "
            "positioning within a specific build"
        )
    )
    multiplier: bpy.props.FloatProperty(
        name="Multiplier",
        default=1,
        min=0.1,
        max=100,
        precision=1,
        step=10,
        description=(
            "Multiplier to increase or decrease the rotation to adjust the "
            "intensity within a specific build"
        )
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
