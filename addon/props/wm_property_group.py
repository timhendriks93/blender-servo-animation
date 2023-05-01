import bpy

from bpy.types import PropertyGroup
from ..ops.start_live_mode import StartLiveMode
from ..utils.live_mode import LiveMode


def get_serial_port_items(_self, _context):
    items = []
    ports = LiveMode.get_serial_ports()

    if len(ports) < 1:
        items.append(("NONE", "No port available", ""))
    else:
        for port in ports:
            items.append((port, port, ""))

    return items


class WindowManagerPropertyGroup(PropertyGroup):
    live_mode_method: bpy.props.EnumProperty(
        name="Method",
        items=StartLiveMode.METHOD_ITEMS
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
    socket_path: bpy.props.StringProperty(
        name="Path",
        default="/"
    )
    position_jump_handling: bpy.props.BoolProperty(
        name="Position Jump Handling",
        description=(
            "Slowly move the servos to their new position "
            "when the position difference exceeds the threshold"
        ),
        default=True
    )
