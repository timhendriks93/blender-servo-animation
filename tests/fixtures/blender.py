import os
import pytest

class Blender:
    file = None
    script = None

    def set_file(self, path):
        self.file = path

    def set_script(self, name):
        self.script = f"tests/blender/{name}"

    def run(self):
        args = f"--background --python-exit-code 1 --python {self.script}"
        command = f"blender {self.file} {args}"
        return os.system(command)

@pytest.fixture
def blender():
    return Blender()
