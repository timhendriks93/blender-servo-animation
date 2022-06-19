import sys
import pathlib
import bpy


def register_vendor_path():
    file_dir = pathlib.Path(__file__).parents[1].absolute()
    vendor_dir = file_dir.joinpath("vendor")
    sys.path.append(str(vendor_dir))


def get_blend_filename():
    return bpy.path.basename(bpy.context.blend_data.filepath)
