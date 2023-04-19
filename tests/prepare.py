import os
import pathlib
import sys
import ensurepip
import subprocess

import bpy


main_dir = pathlib.Path(os.path.dirname(__file__)).resolve()
sys.path.append(str(main_dir))

def ensure_pip():
    ensurepip.bootstrap()
    os.environ.pop("PIP_REQ_TRACKER", None)

def install_dependencies():
    try:
        python = bpy.app.binary_path_python
    except AttributeError:
        python = sys.executable

    dir_path = os.path.dirname(__file__)
    req_file = dir_path + "/../requirements-dev.txt"

    subprocess.run([python, "-m", "pip", "install", "-r", req_file], check=True)

if __name__ == "__main__":
    ensure_pip()
    install_dependencies()
