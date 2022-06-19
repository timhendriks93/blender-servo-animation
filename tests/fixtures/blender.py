import os
import pytest
import pexpect


class Blender:
    file = None
    cwd = None
    spawn = None
    timeout = 3

    def __init__(self):
        self.cwd = os.getcwd()

    def tmp(self, path):
        return self.cwd + "/" + path

    def set_file(self, path):
        self.file = self.cwd + "/" + path

    def start(self):
        args = "--background --addons servo_animation --python-console"
        command = f"blender {self.file} {args}"
        self.spawn = pexpect.spawn(command, timeout=self.timeout)

    def send_lines(self, lines):
        sent_bytes = 0
        for line in lines:
            sent_bytes += self.send_line(line)
        return sent_bytes

    def send_line(self, line):
        return self.spawn.sendline(line)

    def expect(self, line):
        return self.spawn.expect(line)

    def close(self):
        self.spawn.close()


@pytest.fixture
def blender():
    return Blender()
