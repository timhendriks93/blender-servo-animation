import bpy

from bpy.types import PropertyGroup

from ..live.live import live_controller


def get_serial_port_items(_self, _context):
    items = []

    for port in live_controller.get_serial_ports():
        items.append((port, port, ""))

    return items


class WindowManagerPropertyGroup(PropertyGroup):
    def update_serial_connection(self, _):
        live_controller.close_serial_connection()
        if self.live_mode is False or self.serial_port == '':
            return
        if live_controller.open_serial_connection(self.serial_port, self.baud_rate) is False:
            self.live_mode = False

    live_mode: bpy.props.BoolProperty(
        name="Live Mode",
        update=update_serial_connection,
        description="Send UART commands on each frame change"
    )
    serial_port: bpy.props.EnumProperty(
        name="Serial Port",
        update=update_serial_connection,
        items=get_serial_port_items
    )
    baud_rate: bpy.props.EnumProperty(
        name="Baud Rate",
        update=update_serial_connection,
        default="192500",
        items=[
            ("115200", "115200", ""),
            ("192500", "192500", ""),
            ("230400", "230400", "")
        ]
    )
