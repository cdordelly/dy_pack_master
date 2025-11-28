import bpy
import os
import glob
import re
from .. import utils

def localize_vdb():
    """
    Iterates through all volume objects. If a volume is a sequence, it finds all 
    matching files using a regex pattern and copies them. Otherwise, it copies the single VDB file. 
    Finally, it relinks to relative paths.
    """
    base_path = utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing VDB files.")
        return {'CANCELLED'}

    vdb_dir = os.path.join(base_path, "vdb")
    utils.ensure_directory(vdb_dir)
    
    processed_files = set()
    count = 0

    for volume in bpy.data.volumes:
        if not volume.filepath:
            continue

        abs_path = utils.get_absolute_path(volume.filepath)
        abs_path = os.path.normpath(abs_path)
        
        if not os.path.exists(abs_path):
            print(f"WARNING: Source file not found: {abs_path} (Volume: {volume.name})")
            continue

        dir_name = os.path.dirname(abs_path)
        file_name = os.path.basename(abs_path)
        
        files_to_copy = []

        # Check if it's a sequence
        match = re.search(r'(\d+)(?!.*\d)', file_name)
        
        if volume.is_sequence and match:
            prefix = file_name[:match.start()]
            suffix = file_name[match.end():]
            glob_pattern = prefix + "*" + suffix
            search_path = os.path.join(dir_name, glob_pattern)
            
            regex_pattern = re.escape(prefix) + r'\d+' + re.escape(suffix) + "$"
            regex = re.compile(regex_pattern, re.IGNORECASE)
            
            candidates = glob.glob(search_path)
            found_files = []
            
            for cand in candidates:
                cand_name = os.path.basename(cand)
                if regex.match(cand_name):
                    found_files.append(cand)
            
            if found_files:
                files_to_copy = found_files
            else:
                print(f"WARNING: No files found for sequence pattern: {glob_pattern}")
                files_to_copy = [abs_path]
        else:
            files_to_copy = [abs_path]

        # Copy files
        for src_file in files_to_copy:
            src_file = os.path.normpath(src_file)
            if src_file in processed_files:
                continue
                
            utils.copy_file(src_file, vdb_dir)
            processed_files.add(src_file)

        # Relink
        relative_path = f"//vdb/{file_name}"
        if volume.filepath != relative_path:
            volume.filepath = relative_path
            count += 1

    print(f"VDB localization complete. Relinked {count} volumes.")
    return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_vdb(bpy.types.Operator):
    """Localize VDB files to //vdb folder"""
    bl_idname = "dy_pack_master.localize_vdb"
    bl_label = "Localize VDB Files"
    bl_description = "Copy VDB files to //vdb and relink"

    def execute(self, context):
        return localize_vdb()

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_vdb)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_vdb)
