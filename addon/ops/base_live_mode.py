import bpy
from ..utils.live import LIVE_MODE_CONTROLLER


class BaseLiveMode:
    METHOD_SERIAL = "SERIAL"
    METHOD_WEB_SOCKET = "WEB_SOCKET"

    @classmethod
    def poll(cls, context):
        return not context.window_manager.servo_animation.live_mode or bpy.app.background

    @classmethod
    def get_method_items(cls):
        return [
            (cls.METHOD_SERIAL, "Serial", "Connect via USB"),
            (cls.METHOD_WEB_SOCKET, "Web Socket", "Connect via a web socket"),
        ]

    @classmethod
    def register_handlers(cls, context):
        context.window_manager.servo_animation.live_mode = True
        bpy.app.handlers.frame_change_post.append(
            LIVE_MODE_CONTROLLER.update_positions)
        bpy.app.handlers.depsgraph_update_post.append(
            LIVE_MODE_CONTROLLER.update_positions)
        LIVE_MODE_CONTROLLER.update_positions(context.scene, None)
