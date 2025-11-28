import bpy
import os
import shutil
from . import utils

def localize_ocio():
    """
    Checks for the OCIO environment variable, copies the entire OCIO configuration
    directory to a local 'ocio' folder next to the blend file, and creates a text
    file recording the original location.
    """
    base_path = utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing OCIO.")
        return {'CANCELLED'}

    ocio_path = os.environ.get('OCIO')
    if not ocio_path:
        print("WARNING: 'OCIO' environment variable is not set. Nothing to localize.")
        return {'CANCELLED'}

    print(f"Found OCIO environment variable: {ocio_path}")

    if os.path.isfile(ocio_path):
        source_dir = os.path.dirname(ocio_path)
    else:
        source_dir = ocio_path

    if not os.path.exists(source_dir):
        print(f"ERROR: OCIO source directory does not exist: {source_dir}")
        return {'CANCELLED'}

    dest_dir = os.path.join(base_path, "ocio")

    try:
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
    except OSError as e:
        print(f"ERROR: Failed to copy OCIO directory: {e}")
        return {'CANCELLED'}

    info_file_path = os.path.join(dest_dir, "_OCIO_original_location.txt")
    try:
        with open(info_file_path, "w") as f:
            f.write("OCIO localization info:\n")
            f.write(f"OCIO config file copy from: {ocio_path}\n")
            f.write(f"OCIO config file source Directory: {source_dir}\n")
    except OSError as e:
        print(f"WARNING: Failed to create info file: {e}")

    if os.path.isfile(ocio_path):
        config_filename = os.path.basename(ocio_path)
    else:
        config_filename = "config.ocio"

    bat_file_path = os.path.join(dest_dir, "set_OCIO_env.bat")
    bat_content = f"""@echo off
reg add "HKCU\\Environment" /v "OCIO" /t REG_SZ /d "%~dp0{config_filename}" /f
"""
    try:
        with open(bat_file_path, "w") as f:
            f.write(bat_content)
    except OSError as e:
        print(f"WARNING: Failed to create batch file: {e}")

    sh_file_path = os.path.join(dest_dir, "set_OCIO_env.sh")
    sh_content = f"""#!/bin/bash
export OCIO="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)/{config_filename}"
echo "OCIO environment variable set to: $OCIO"
"""
    try:
        with open(sh_file_path, "w") as f:
            f.write(sh_content)
        try:
            os.chmod(sh_file_path, 0o755)
        except:
            pass
    except OSError as e:
        print(f"WARNING: Failed to create shell script: {e}")

    print("OCIO localization complete.")
    return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_ocio(bpy.types.Operator):
    """Localize OCIO Configuration"""
    bl_idname = "dy_pack_master.localize_ocio"
    bl_label = "Localize OCIO"
    bl_description = "Copy OCIO config to //ocio and create setup scripts"

    def execute(self, context):
        return localize_ocio()

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_ocio)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_ocio)
