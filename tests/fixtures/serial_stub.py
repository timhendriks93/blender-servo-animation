import os
import pty
import pytest


class SerialStub:
    receiver = None
    sender = None

    def open(self):
        self.receiver, self.sender = pty.openpty()

        return os.ttyname(self.sender)

    def read_bytes(self):
        read_bytes = []

        try:
            os.close(self.sender)
            with os.fdopen(self.receiver, "rb") as reader:
                while len(reader.peek()) > 0:
                    byte = reader.read(1)
                    read_bytes.append(byte)
        except OSError:
            pass

        return read_bytes


@pytest.fixture
def serial_stub():
    return SerialStub()
