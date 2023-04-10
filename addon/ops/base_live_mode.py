import bpy

def handle_live_mode(_scene, _depsgraph):
    servo_animation = bpy.context.window_manager.servo_animation

    if servo_animation.live_mode_handling:
        return

    servo_animation.live_mode_handling = True
    bpy.ops.export_anim.live_mode()
    servo_animation.live_mode_handling = False

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
    def register_handlers(cls):
        bpy.context.window_manager.servo_animation.live_mode = True
        bpy.app.handlers.frame_change_post.append(handle_live_mode)
        bpy.app.handlers.depsgraph_update_post.append(handle_live_mode)
        handle_live_mode(bpy.context.scene, None)

    @classmethod
    def unregister_handlers(cls):
        bpy.context.window_manager.servo_animation.live_mode = False
        bpy.app.handlers.frame_change_post.remove(handle_live_mode)
        bpy.app.handlers.depsgraph_update_post.remove(handle_live_mode)
