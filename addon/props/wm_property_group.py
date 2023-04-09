import bpy

from bpy.types import PropertyGroup
from ..utils.web import is_ip
from ..utils.uart import get_serial_ports
from ..utils.live import METHOD_SERIAL, METHOD_WEB_SOCKET


def get_serial_port_items(_self, _context):
    items = []

    for port in get_serial_ports():
        items.append((port, port, ""))

    return items


def set_ip_address(self, value):
    if not is_ip(value):
        raise ValueError("Invalid IP address")
    self.ip_address = value


def get_ip_address(self):
    return self.ip_address


class WindowManagerPropertyGroup(PropertyGroup):
    live_mode: bpy.props.BoolProperty(
        name="Live Mode"
    )
    live_mode_method: bpy.props.EnumProperty(
        name="Method",
        items=[
            (METHOD_SERIAL, "Serial", "Connect via USB"),
            (METHOD_WEB_SOCKET, "Web Socket", "Connect via a web socket"),
        ],
        default=0
    )
    serial_port: bpy.props.EnumProperty(
        name="Serial Port",
        items=get_serial_port_items
    )
    baud_rate: bpy.props.EnumProperty(
        name="Baud Rate",
        default="115200",
        items=[
            ("19200", "19200", ""),
            ("115200", "115200", ""),
            ("192500", "192500", "")
        ]
    )
    ip_address: bpy.props.StringProperty(
        default="127.0.0.1"
    )
    socket_ip: bpy.props.StringProperty(
        name="IP Address",
        get=get_ip_address,
        set=set_ip_address
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
