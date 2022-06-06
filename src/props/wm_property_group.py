import bpy

from bpy.types import PropertyGroup

from ..utils.uart import UART_CONTROLLER


def get_serial_port_items(_self, _context):
    items = []

    for port in UART_CONTROLLER.get_serial_ports():
        items.append((port, port, ""))

    return items


def close_serial_connection(_self, _context):
    UART_CONTROLLER.close_serial_connection()


def toggle_serial_connection(self, context):
    close_serial_connection(self, context)

    if not self.live_mode or self.serial_port == '':
        return

    if UART_CONTROLLER.open_serial_connection():
        UART_CONTROLLER.update_positions(context.scene)
    else:
        self.live_mode = False


class WindowManagerPropertyGroup(PropertyGroup):
    live_mode: bpy.props.BoolProperty(
        name="Live Mode",
        update=toggle_serial_connection,
        description="Send UART commands on each frame change"
    )
    serial_port: bpy.props.EnumProperty(
        name="Serial Port",
        update=close_serial_connection,
        items=get_serial_port_items
    )
    baud_rate: bpy.props.EnumProperty(
        name="Baud Rate",
        update=close_serial_connection,
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
