import os
import sys
import subprocess
import ensurepip
import bpy

from bpy.types import Operator
from ..ops.live_mode import LiveMode


class InstallDependencies(Operator):
    bl_idname = "wm.install_servo_animation_deps"
    bl_label = "Install Servo Animation Live Mode Dependencies"
    bl_description ="Install missing live mode dependencies (requires an active internet connection)"
    bl_options = {'INTERNAL', 'BLOCKING'}

    python: bpy.props.StringProperty()

    @classmethod
    def poll(cls, _context):
        return not LiveMode.is_available()

    def execute(self, _context):
        try:
            self.install_pip()
            self.install_requirements()
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({"ERROR"}, str(err))

            return {"CANCELLED"}

        LiveMode.update_dependencies()

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
