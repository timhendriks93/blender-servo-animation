import threading
import pytest

from websockets.sync.server import serve

class SocketStub:
    host = None
    port = None
    server = None
    server_thread = None
    received_data = []

    def __init__(self):
        self.received_data = []
        self.server = serve(self.handler, "localhost", 0)
        self.host, self.port = self.server.socket.getsockname()
        self.server_thread = threading.Thread(target=self.run)

    def start(self):
        self.server_thread.start()

    def run(self):
        self.server.serve_forever()

    def handler(self, websocket):
        for message in websocket:
            for integer in message:
                byte = integer.to_bytes(length=1, byteorder='big')
                self.received_data.append(byte)

    def close(self):
        self.server.shutdown()
        self.server_thread.join()

@pytest.fixture()
def socket_stub():
    return SocketStub()
