import bpy
import os
from . import utils

def missing_files_report(operator=None, base_path=None):
    """Checks for missing files and generates a report if any are found."""
    base_path = base_path or utils.get_blend_dir()
    if not base_path:
        if operator:
            operator.report({'ERROR'}, "Save blend file first!")
        else:
            print("ERROR: Blend file must be saved before checking for missing files.")
        return {'CANCELLED'}

    missing_files = []

    def check_file(filepath, name, type_label):
        if not filepath:
            return
        abs_path = os.path.normpath(utils.get_absolute_path(filepath))
        if not os.path.exists(abs_path):
            missing_files.append(f"[{type_label}] {name}: {abs_path}")

    try:
        bpy.ops.file.report_missing_files()
    except:
        pass

    for img in bpy.data.images:
        if img.source in {'FILE', 'SEQUENCE'} and not img.packed_file:
            check_file(img.filepath, img.name, "Image")

    for lib in bpy.data.libraries:
        check_file(lib.filepath, lib.name, "Library")

    for cache in bpy.data.cache_files:
        check_file(cache.filepath, cache.name, "Cache")

    if missing_files:
        report_path = os.path.join(base_path, "missing_files_report.txt")
        try:
            with open(report_path, "w") as f:
                f.write("Missing Files Report\n")
                f.write("====================\n")
                f.write(f"Source Blend: {bpy.data.filepath}\n\n")
                f.write("\n".join(missing_files))
            if operator:
                operator.report({'WARNING'}, f"Found {len(missing_files)} missing files! Report saved.")
            else:
                print(f"FOUND {len(missing_files)} missing files. Report: {report_path}")
        except OSError as e:
            if operator:
                operator.report({'ERROR'}, f"Failed to write report: {e}")
            else:
                print(f"ERROR: Failed to write report: {e}")
    else:
        if operator:
            operator.report({'INFO'}, "No missing files found.")
        else:
            print("No missing files found.")

    return {'FINISHED'}

class DY_PACK_MASTER_OT_missing_files_report(bpy.types.Operator):
    """Generate Missing Files Report"""
    bl_idname = "dy_pack_master.missing_files_report"
    bl_label = "Missing Files Report"
    bl_description = "Check for missing external files and generate a report"

    def execute(self, context):
        return missing_files_report(self)

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_missing_files_report)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_missing_files_report)