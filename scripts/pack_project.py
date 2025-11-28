import bpy
from .modules import mesh_sequence_cache
from .modules import vdb
from .modules import references
from .modules import render_settings
from .modules import report
from .modules import utils

def pack_project():
    """
    Main packing function that executes all localization steps:
    1. Pack blend file resources
    2. Localize mesh caches (ABC/USD)
    3. Localize references
    4. Localize VDBs
    5. Set relative output path
    6. Generate missing files report
    7. Save blend with suffix from preferences
    """
    # Get preferences
    prefs = bpy.context.preferences.addons['dy_pack_master'].preferences
    blend_suffix = prefs.blend_suffix
    
    print("=" * 50)
    print("dy Pack Master - Pack Project")
    print("=" * 50)
    
    # 1. Pack all blend file resources
    print("\n[1/7] Packing blend file resources...")
    bpy.ops.file.pack_all()
    
    # 2. Localize Mesh Caches (ABC/USD)
    print("\n[2/7] Localizing Mesh Caches (ABC/USD)...")
    mesh_sequence_cache.localize_mesh_cache()
    
    # 3. Localize References
    print("\n[3/7] Localizing References...")
    references.localize_references()
    
    # 4. Localize VDBs
    print("\n[4/7] Localizing VDBs...")
    vdb.localize_vdb()
    
    # 5. Set Relative Output Path
    print("\n[5/7] Setting relative output path...")
    render_settings.set_relative_output()
    
    # 6. Generate Missing Files Report
    print("\n[6/7] Generating missing files report...")
    report.missing_files_report()
    
    # 7. Save with suffix from preferences
    print(f"\n[7/7] Saving blend file with '{blend_suffix}' suffix...")
    new_filepath = utils.save_blend_with_suffix(blend_suffix)
    
    print("\n" + "=" * 50)
    print("Pack Project Complete!")
    print("=" * 50)
    
    return {'FINISHED'}, new_filepath

class DY_PACK_MASTER_OT_pack_project(bpy.types.Operator):
    """Pack and localize entire project for render farm"""
    bl_idname = "dy_pack_master.pack_project"
    bl_label = "Pack Project"
    
    @classmethod
    def description(cls, context, properties):
        prefs = context.preferences.addons['dy_pack_master'].preferences
        return f"One-click: Pack resources, localize assets, and save as blend file with '{prefs.blend_suffix}' suffix"

    def execute(self, context):
        result, new_filepath = pack_project()
        
        # Show success message
        if new_filepath:
            self.report({'INFO'}, f"Project packed: {new_filepath}")
        else:
            self.report({'INFO'}, "Project packed successfully")
        
        return result

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_pack_project)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_pack_project)
