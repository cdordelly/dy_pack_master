import bpy
from .modules import mesh_sequence_cache
from .modules import vdb
from .modules import references
from .modules import render_settings
from .modules import report
from .modules import utils

# Get the addon package name for preferences lookup
ADDON_NAME = __package__.rsplit('.', 1)[0] if '.' in __package__ else __package__

def pack_project():
    """
    Main packing function that executes all localization steps:
    
    1. Convert all asset paths to absolute
    2. Create pack directory and save blend file there
    3. Pack blend file resources
    4. Localize mesh caches (ABC/USD)
    5. Localize references
    6. Localize VDBs
    7. Set relative output path
    8. Generate missing files report
    9. Final save
    """
    # Validate blend file is saved
    if not bpy.data.filepath:
        print("ERROR: Blend file must be saved before packing.")
        return {'CANCELLED'}, None
    
    # Get preferences
    prefs = bpy.context.preferences.addons[ADDON_NAME].preferences
    blend_suffix = prefs.blend_suffix
    
    print("=" * 50)
    print("dy Pack Master - Pack Project")
    print("=" * 50)
    
    # Step 1: Convert all asset paths to absolute
    print("\n[1/9] Converting asset paths to absolute...")
    utils.convert_all_paths_to_absolute()
    
    # Step 2: Create pack directory and save blend file there
    print(f"\n[2/9] Creating pack directory and saving blend file...")
    new_filepath = utils.save_blend_to_pack_directory(blend_suffix)
    if not new_filepath:
        print("ERROR: Failed to create pack directory and save blend file.")
        return {'CANCELLED'}, None
    
    # Step 3: Pack all blend file resources
    print("\n[3/9] Packing blend file resources...")
    bpy.ops.file.pack_all()
    
    # Step 4: Localize Mesh Caches (ABC/USD)
    print("\n[4/9] Localizing Mesh Caches (ABC/USD)...")
    mesh_sequence_cache.localize_mesh_cache()
    
    # Step 5: Localize References
    print("\n[5/9] Localizing References...")
    references.localize_references()
    
    # Step 6: Localize VDBs
    print("\n[6/9] Localizing VDBs...")
    vdb.localize_vdb()
    
    # Step 7: Set Relative Output Path
    print("\n[7/9] Setting relative output path...")
    render_settings.set_relative_output()
    
    # Step 8: Generate Missing Files Report
    print("\n[8/9] Generating missing files report...")
    report.missing_files_report()
    
    # Step 9: Final save
    print("\n[9/9] Saving final packed blend file...")
    bpy.ops.wm.save_mainfile()
    
    print("\n" + "=" * 50)
    print("Pack Project Complete!")
    print(f"Packed project: {new_filepath}")
    print("=" * 50)
    
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
        
        # Show success message
        if new_filepath:
            self.report({'INFO'}, f"Project packed: {new_filepath}")
        else:
            self.report({'ERROR'}, "Pack project failed")
        
        return result

# -------------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------------

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_pack_project)


def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_pack_project)