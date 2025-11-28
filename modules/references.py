import bpy
import os
import shutil
from .. import utils

def localize_references():
    """
    Iterates through all linked libraries, copies the referenced blend files to a 
    local 'references' folder, handles duplicate filenames by renaming, relinks 
    the libraries to the new relative paths, and generates a report.
    """
    base_path = utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing references.")
        return {'CANCELLED'}

    refs_dir = os.path.join(base_path, "references")
    utils.ensure_directory(refs_dir)

    processed_libs = {}
    used_filenames = set()
    
    report_lines = []
    report_lines.append("Reference Localization Report")
    report_lines.append("=============================")
    report_lines.append(f"Source Blend: {bpy.data.filepath}")
    report_lines.append("")

    for lib in bpy.data.libraries:
        if not lib.filepath:
            continue
            
        normalized_path = lib.filepath.replace('\\', '/')
        if normalized_path.startswith("//references"):
            continue

        source_abs_path = utils.get_absolute_path(lib.filepath)
        source_abs_path = os.path.normpath(source_abs_path)

        if not os.path.exists(source_abs_path):
            print(f"WARNING: Source library not found: {source_abs_path} (Library: {lib.name})")
            report_lines.append(f"[MISSING] {lib.name} -> {source_abs_path}")
            continue

        if source_abs_path in processed_libs:
            dest_filename = processed_libs[source_abs_path]
        else:
            original_filename = os.path.basename(source_abs_path)
            name, ext = os.path.splitext(original_filename)
            
            dest_filename = original_filename
            counter = 1
            
            while dest_filename in used_filenames:
                dest_filename = f"{name}_{counter:03d}{ext}"
                counter += 1
            
            used_filenames.add(dest_filename)
            processed_libs[source_abs_path] = dest_filename
            
            dest_filepath = os.path.join(refs_dir, dest_filename)
            
            try:
                shutil.copy2(source_abs_path, dest_filepath)
                report_lines.append(f"[COPIED] {dest_filename} <- {source_abs_path}")
            except OSError as e:
                print(f"ERROR: Failed to copy {source_abs_path}: {e}")
                report_lines.append(f"[ERROR] Copy failed: {source_abs_path} -> {e}")
                continue

        relative_path = f"//references/{dest_filename}"
        
        if lib.filepath != relative_path:
            old_path = lib.filepath
            lib.filepath = relative_path
            try:
                lib.reload()
                print(f"Relinked library {lib.name}: {old_path} -> {relative_path}")
            except Exception as e:
                print(f"WARNING: Failed to reload library {lib.name}: {e}")
                report_lines.append(f"[WARNING] Reload failed: {lib.name}")

    report_path = os.path.join(refs_dir, "references_report.txt")
    try:
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
        print(f"Report generated: {report_path}")
    except OSError as e:
        print(f"WARNING: Failed to write report: {e}")

    print("Reference localization complete.")
    return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_references(bpy.types.Operator):
    """Localize Linked Libraries to //references folder"""
    bl_idname = "dy_pack_master.localize_references"
    bl_label = "Localize References"
    bl_description = "Copy linked .blend files to //references and relink"

    def execute(self, context):
        return localize_references()

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_references)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_references)
