import socket
import threading
import pytest

class SocketStub:
    host = None
    port = None
    sock = None
    server_thread = None
    received_data = []

    def __init__(self):
        self.received_data = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("localhost", 0))
        self.host, self.port = self.sock.getsockname()

        self.server_thread = threading.Thread(target=self.handle_tcp)
        self.server_thread.start()

    def __del__(self):
        self.sock.close()
        self.server_thread.join()

    def handle_tcp(self):
        self.sock.listen(1)
        conn, _addr = self.sock.accept()
        with conn:
            while True:
                byte = conn.recv(1)
                if not byte:
                    break
                self.received_data.append(byte)

@pytest.fixture()
def socket_stub():
    return SocketStub()
