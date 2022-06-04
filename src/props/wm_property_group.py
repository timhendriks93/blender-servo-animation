import bpy

from bpy.types import PropertyGroup

from ..utils.uart import UART_CONTROLLER


def get_serial_port_items(_self, _context):
    items = []

    for port in UART_CONTROLLER.get_serial_ports():
        items.append((port, port, ""))

    return items


class WindowManagerPropertyGroup(PropertyGroup):
    def update_serial_connection(self, context):
        UART_CONTROLLER.close_serial_connection()
        if self.live_mode is False or self.serial_port == '':
            return
        if UART_CONTROLLER.open_serial_connection() is False:
            self.live_mode = False
        UART_CONTROLLER.on_frame_change_post(context.scene)

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
        default="115200",
        items=[
            ("19200", "19200", ""),
            ("115200", "115200", ""),
            ("192500", "192500", "")
        ]
    )
    frame_jump_handling: bpy.props.BoolProperty(
        name="Frame Jump Handling",
        description="Slowly move the servos to their new position when jumping between frames",
        default=True
    )
