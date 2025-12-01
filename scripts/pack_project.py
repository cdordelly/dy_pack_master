import bpy
import os
import platform
from datetime import datetime
from .modules import mesh_sequence_cache, vdb, references, render_settings, report, utils, images, movies

# Get the addon package name for preferences lookup
ADDON_NAME = __package__.rsplit('.', 1)[0] if '.' in __package__ else __package__

def pack_project():
    """Main packing function that executes all localization steps."""
    if not bpy.data.filepath:
        print("ERROR: Blend file must be saved before packing.")
        return {'CANCELLED'}, None
    
    prefs = bpy.context.preferences.addons[ADDON_NAME].preferences
    blend_suffix = prefs.blend_suffix
    if not blend_suffix.startswith('_'):
        blend_suffix = '_' + blend_suffix
    
    # Store original filepath to potentially reopen later
    original_filepath = bpy.data.filepath
    
    # Determine pack directory and log path
    directory = os.path.dirname(bpy.data.filepath)
    filename = os.path.basename(bpy.data.filepath)
    name = os.path.splitext(filename)[0]
    packed_dir = os.path.join(directory, f"{name}{blend_suffix}")
    log_path = os.path.join(packed_dir, "pack_log.txt")
    new_filepath = os.path.join(packed_dir, f"{name}{blend_suffix}.blend")
    
    # Create pack directory first (needed for log file)
    utils.ensure_directory(packed_dir)
    
    with utils.log_to_file(log_path):
        # Log header with system info
        print("Pack Log - dy Pack Master")
        print("=" * 50)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"OS: {platform.system()} {platform.release()}")
        print(f"Blender: {bpy.app.version_string}")
        print(f"Source File: {original_filepath}")
        print(f"Pack Directory: {packed_dir}")
        print(f"OCIO Config: {os.environ.get('OCIO', 'Default (Blender built-in)')}")
        print("=" * 50)
        print()

        print("=" * 50)
        print("dy Pack Master - Pack Project")
        print("=" * 50)

        print("\n[0/11] Saving current blend file...")
        bpy.ops.wm.save_mainfile()
        
        print("\n[1/11] Converting asset paths to absolute...")
        utils.convert_all_paths_to_absolute()
        
        print("\n[2/11] Saving to pack directory (switching to packed file)...")
        try:
            bpy.ops.wm.save_as_mainfile(filepath=new_filepath, copy=False)
            print(f"  - Now working in: {new_filepath}")
        except Exception as e:
            print(f"ERROR: Failed to save file: {e}")
            return {'CANCELLED'}, None
        
        print("\n[3/11] Packing blend file resources...")
        bpy.ops.file.pack_all()
        
        print("\n[4/11] Localizing Images (Sequences & Movies)...")
        images.localize_images(base_path=packed_dir)

        print("\n[5/11] Localizing Movie Clips...")
        movies.localize_movieclips(base_path=packed_dir)
        
        print("\n[6/11] Localizing Mesh Caches (ABC/USD)...")
        mesh_sequence_cache.localize_mesh_cache(base_path=packed_dir)
        
        print("\n[7/11] Localizing References...")
        references.localize_references(base_path=packed_dir)
        
        print("\n[8/11] Localizing VDBs...")
        vdb.localize_vdb(base_path=packed_dir)
        
        print("\n[9/11] Setting relative output path...")
        render_settings.set_relative_output()
        
        print("\n[10/11] Generating missing files report...")
        report.missing_files_report(base_path=packed_dir)
        
        print("\n[11/11] Saving final packed blend file...")
        bpy.ops.wm.save_mainfile()
        
        print("\n" + "=" * 50)
        print("Pack Project Complete!")
        print(f"Packed project: {new_filepath}")
        print("=" * 50)
    
    # Optionally reopen original file
    if prefs.reopen_original_file:
        print(f"\nReopening original file: {original_filepath}")
        bpy.ops.wm.open_mainfile(filepath=original_filepath)

    # Optionally open directory after pack
    if prefs.open_directory_after_pack:
        pack_dir = os.path.dirname(new_filepath)
        utils.open_directory(pack_dir)
    
    return {'FINISHED'}, new_filepath

class DY_PACK_MASTER_OT_pack_project(bpy.types.Operator):
    """Pack and localize entire project for render farm"""
    bl_idname = "dy_pack_master.pack_project"
    bl_label = "Pack Project"
    
    @classmethod
    def description(cls, context, properties):
        prefs = context.preferences.addons.get(ADDON_NAME)
        if prefs:
            suffix = prefs.preferences.blend_suffix
            return f"One-click: Convert paths, create '{suffix}' folder, pack resources, and localize all assets"
        return "One-click: Pack resources, localize assets, and save blend file"

    def execute(self, context):
        result, new_filepath = pack_project()
        if new_filepath:
            self.report({'INFO'}, f"Project packed: {new_filepath}")
        else:
            self.report({'ERROR'}, "Pack project failed")
        return result

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_pack_project)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_pack_project)