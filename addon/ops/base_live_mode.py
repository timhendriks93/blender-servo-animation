class BaseLiveMode:
    METHOD_SERIAL = "SERIAL"
    METHOD_WEB_SOCKET = "WEB_SOCKET"

    @classmethod
    def get_method_items(cls):
        return [
            (cls.METHOD_SERIAL, "Serial", "Connect via USB"),
            (cls.METHOD_WEB_SOCKET, "Web Socket", "Connect via a web socket"),
        ]
