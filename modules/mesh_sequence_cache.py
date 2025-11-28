import bpy
import os
from .. import utils

def localize_mesh_cache():
    """
    Iterates through all objects, finds Mesh Sequence Cache modifiers (Alembic/USD),
    copies the referenced files to local 'abc' or 'usd' folders, and relinks them relatively.
    """
    base_path = utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing cache files.")
        return {'CANCELLED'}

    processed_caches = set()
    count = 0

    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type == 'MESH_SEQUENCE_CACHE':
                cache_file = mod.cache_file
                if not cache_file:
                    continue

                if cache_file in processed_caches:
                    continue
                
                current_filepath = utils.get_absolute_path(cache_file.filepath)
                
                if not os.path.exists(current_filepath):
                    print(f"WARNING: Source file not found: {current_filepath} (Object: {obj.name})")
                    continue
                
                # Determine type and destination
                ext = os.path.splitext(current_filepath)[1].lower()
                if ext in {'.abc'}:
                    subfolder = "abc"
                elif ext in {'.usd', '.usda', '.usdc', '.usdz'}:
                    subfolder = "usd"
                else:
                    print(f"WARNING: Unknown cache format '{ext}' for {current_filepath}")
                    continue

                dest_dir = os.path.join(base_path, subfolder)
                utils.ensure_directory(dest_dir)

                # Copy file
                dest_path = utils.copy_file(current_filepath, dest_dir)
                if not dest_path:
                    continue

                # Relink
                filename = os.path.basename(dest_path)
                relative_path = f"//{subfolder}/{filename}"
                
                if cache_file.filepath != relative_path:
                    cache_file.filepath = relative_path
                    count += 1
                
                processed_caches.add(cache_file)

    print(f"Mesh Cache localization complete. Relinked {count} files.")
    return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_mesh_cache(bpy.types.Operator):
    """Localize Alembic and USD files"""
    bl_idname = "dy_pack_master.localize_mesh_cache"
    bl_label = "Localize Mesh Cache (ABC/USD)"
    bl_description = "Copy Alembic/USD files to //abc or //usd and relink"

    def execute(self, context):
        return localize_mesh_cache()

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_mesh_cache)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_mesh_cache)
