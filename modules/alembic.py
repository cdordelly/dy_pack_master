import bpy
import os
from .. import utils

def localize_alembics():
    """
    Iterates through all objects, finds Alembic modifiers, copies the referenced
    Alembic files to a local 'abc' folder, and relinks them relatively.
    """
    base_path = utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing Alembic files.")
        return {'CANCELLED'}

    abc_dir = os.path.join(base_path, "abc")
    utils.ensure_directory(abc_dir)

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

                # Copy file
                dest_path = utils.copy_file(current_filepath, abc_dir)
                if not dest_path:
                    continue

                # Relink
                filename = os.path.basename(dest_path)
                relative_path = f"//abc/{filename}"
                
                if cache_file.filepath != relative_path:
                    cache_file.filepath = relative_path
                    count += 1
                
                processed_caches.add(cache_file)

    print(f"Alembic localization complete. Relinked {count} files.")
    return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_abc(bpy.types.Operator):
    """Localize Alembic files to //abc folder"""
    bl_idname = "dy_pack_master.localize_abc"
    bl_label = "Localize Alembic Files"
    bl_description = "Copy Alembic files to //abc and relink"

    def execute(self, context):
        return localize_alembics()

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_abc)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_abc)
