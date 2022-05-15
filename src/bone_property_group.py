import bpy

from bpy.types import PropertyGroup


class ServoAnimationBonePropertyGroup(PropertyGroup):
    def range_limit_value(self, value, min_value, max_value):
        if min_value is not None and value < min_value:
            return min_value
        elif max_value is not None and value > max_value:
            return max_value
        else:
            return value

    def update_position_min(self, _context):
        self["position_min"] = self.range_limit_value(
            self.position_min, None, self.position_max)

    def update_position_max(self, _context):
        self["position_max"] = self.range_limit_value(
            self.position_max, self.position_min, None)

    def update_position_limit_start(self, _context):
        self["position_limit_start"] = self.range_limit_value(
            self.position_limit_start, self.position_min, self.position_limit_end)

    def update_position_limit_end(self, _context):
        self["position_limit_end"] = self.range_limit_value(
            self.position_limit_end, self.position_limit_start, self.position_max)

    def update_neutral_angle(self, _context):
        self["neutral_angle"] = self.range_limit_value(
            self.neutral_angle, None, self.rotation_range)

    active: bpy.props.BoolProperty(
        name="Provide Servo Settings",
        description="Provide servo settings for this bone"
    )
    servo_id: bpy.props.IntProperty(
        name="Servo ID",
        default=0,
        min=0,
        max=256,
        description="The unique servo ID used to send live data via UART"
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
        description=(
            "The minimum position value before the servo is "
            "supposed to stop moving within a specific build"
        )
    )
    position_limit_end: bpy.props.IntProperty(
        name="Position Limit End",
        default=600,
        min=0,
        max=10000,
        description=(
            "The maximum position value before the servo is supposed to "
            "stop moving within a specific build"
        )
    )
    neutral_angle: bpy.props.IntProperty(
        name="Neutral Angle",
        default=90,
        min=0,
        max=360,
        description=(
            "The assumed neutral angle of the servo in degrees (typically half the rotation range) "
            "which should be adjusted carefully, since the servo will first move to its 'natural' "
            "neutral angle when powered"
        )
    )
    reverse_direction: bpy.props.BoolProperty(
        name="Reverse Direction",
        description=(
            "Whether the applied rotation should be reversed when converting to "
            "position value which might be necessary to reflect the servo's "
            "positioning within a specific build"
        )
    )
    set_position_limits: bpy.props.BoolProperty(
        name="Set Position Limits",
        description=(
            "Define a position range to limit the calculated position values "
            "according to a specific build"
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
            "Multilplier to increase or decrease the rotation to adjust the "
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
