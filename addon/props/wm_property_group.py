import bpy

from bpy.types import PropertyGroup
from ..ops.live_mode import LiveMode


def get_serial_port_items(_self, _context):
    items = []

    for port in LiveMode.get_serial_ports():
        items.append((port, port, ""))

    return items


class WindowManagerPropertyGroup(PropertyGroup):
    live_mode_method: bpy.props.EnumProperty(
        name="Method",
        items=LiveMode.METHOD_ITEMS
    )
    serial_port: bpy.props.EnumProperty(
        name="Port",
        items=get_serial_port_items
    )
    serial_baud: bpy.props.EnumProperty(
        name="Baud Rate",
        default="115200",
        items=[
            ("19200", "19200", ""),
            ("115200", "115200", ""),
            ("192500", "192500", "")
        ]
    )
    socket_host: bpy.props.StringProperty(
        name="Host",
        default="127.0.0.1"
    )
    socket_port: bpy.props.IntProperty(
        name="Port",
        min=0,
        max=65535,
        default=80
    )
    position_jump_handling: bpy.props.BoolProperty(
        name="Position Jump Handling",
        description=(
            "Slowly move the servos to their new position "
            "when the position difference exceeds the threshold"
        ),
        default=True
    )
    position_jump_threshold: bpy.props.IntProperty(
        name="Threshold",
        default=20,
        min=2,
        max=100,
        description="The position difference value triggering position jump handling when exceeded"
    )
