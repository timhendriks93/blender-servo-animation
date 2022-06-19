import bpy

from bpy.types import PropertyGroup
from ..utils.uart import UART_CONTROLLER


def get_serial_port_items(_self, _context):
    items = []

    for port in UART_CONTROLLER.get_serial_ports():
        items.append((port, port, ""))

    return items


def stop_live_mode(self, _context):
    if self.live_mode:
        bpy.ops.export_anim.stop_live_mode()


class WindowManagerPropertyGroup(PropertyGroup):
    live_mode: bpy.props.BoolProperty(
        name="Live Mode"
    )
    serial_port: bpy.props.EnumProperty(
        name="Serial Port",
        update=stop_live_mode,
        items=get_serial_port_items
    )
    baud_rate: bpy.props.EnumProperty(
        name="Baud Rate",
        update=stop_live_mode,
        default="115200",
        items=[
            ("19200", "19200", ""),
            ("115200", "115200", ""),
            ("192500", "192500", "")
        ]
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
