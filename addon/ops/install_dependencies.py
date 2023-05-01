import os
import sys
import subprocess
import ensurepip

from importlib.util import find_spec
from bpy.types import Operator

import bpy


class InstallDependencies(Operator):
    bl_idname = "servo_animation.install_dependencies"
    bl_label = "Install Servo Animation Live Mode Dependencies"
    bl_description ="Install missing live mode dependencies (requires an active internet connection)"
    bl_options = {'INTERNAL', 'BLOCKING'}

    MODULES = ["serial", "websocket"]

    python: bpy.props.StringProperty()

    @classmethod
    def poll(cls, _context):
        return not cls.installed()

    @classmethod
    def installed(cls):
        for module in cls.MODULES:
            if find_spec(module) is None:
                return False

        return True

    def execute(self, _context):
        try:
            self.install_pip()
            self.install_requirements()
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({"ERROR"}, str(err))

            return {"CANCELLED"}

        return {"FINISHED"}

    def install_pip(self):
        try:
            subprocess.run([self.python, "-m", "pip", "--version"], check=True)
        except subprocess.CalledProcessError:
            ensurepip.bootstrap()
            os.environ.pop("PIP_REQ_TRACKER", None)

    def install_requirements(self):
        file_path = os.path.realpath(__file__)
        dir_path = os.path.dirname(file_path)
        req_file = dir_path + "/../requirements.txt"

        subprocess.run([self.python, "-m", "pip", "install", "-r", req_file], check=True)

    def invoke(self, context, _event):
        try:
            self.python = bpy.app.binary_path_python
        except AttributeError:
            self.python = sys.executable

        return self.execute(context)
