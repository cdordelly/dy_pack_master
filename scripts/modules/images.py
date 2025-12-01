import bpy
import os
import glob
import re
from . import utils

def set_absolute_path_images():
    """Converts the filepath of all image sequences and movies to an absolute path."""
    items_to_process = []
    for img in bpy.data.images:
        if img.source not in {'SEQUENCE', 'MOVIE'} or img.packed_file or not img.filepath:
            continue
            
        abs_path = utils.get_absolute_path(img.filepath)
        if img.filepath != abs_path:
            img.filepath = abs_path
            
        items_to_process.append(img)
    
    return items_to_process

def localize_images(base_path=None, source_filter=None):
    """
    Copies image sequence and movie files to local folders and relinks them relatively.
    source_filter: None = all, 'SEQUENCE', or 'MOVIE'
    """
    base_path = base_path or utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing images.")
        return {'CANCELLED'}

    # Check if there are any image sequences or movies to process
    sequences_to_process = []
    movies_to_process = []
    
    for img in bpy.data.images:
        if img.packed_file or not img.filepath:
            continue
        normalized_path = img.filepath.replace('\\', '/')
        
        if img.source == 'SEQUENCE' and source_filter in (None, 'SEQUENCE'):
            if not normalized_path.startswith("//sequences"):
                sequences_to_process.append(img)
        elif img.source == 'MOVIE' and source_filter in (None, 'MOVIE'):
            if not normalized_path.startswith("//movies"):
                movies_to_process.append(img)
    
    # Early exit if nothing to localize
    if not sequences_to_process and not movies_to_process:
        print("No image sequences or movies found to localize.")
        return {'FINISHED'}

    processed_files = set()
    count = 0

    # Process image sequences
    if sequences_to_process:
        sequences_dir = os.path.join(base_path, "sequences")
        utils.ensure_directory(sequences_dir)
        
        for img in sequences_to_process:
            abs_path = utils.get_absolute_path(img.filepath)
            abs_path = os.path.normpath(abs_path)
            
            if not os.path.exists(abs_path):
                print(f"WARNING: Source file not found: {abs_path} (Image: {img.name})")
                continue

            dir_name = os.path.dirname(abs_path)
            file_name = os.path.basename(abs_path)
            
            files_to_copy = []

            # Find the last group of digits in the filename (frame number)
            match = re.search(r'(\d+)(?!.*\d)', file_name)
            
            if match:
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
                    print(f"  - Found {len(found_files)} files for sequence: {img.name}")
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
                    
                utils.copy_file(src_file, sequences_dir)
                processed_files.add(src_file)

            # Relink
            relative_path = f"//sequences/{file_name}"
            if img.filepath != relative_path:
                img.filepath = relative_path
                count += 1

    # Process movies
    if movies_to_process:
        movies_dir = os.path.join(base_path, "movies")
        utils.ensure_directory(movies_dir)
        
        for img in movies_to_process:
            abs_path = utils.get_absolute_path(img.filepath)
            abs_path = os.path.normpath(abs_path)
            
            if not os.path.exists(abs_path):
                print(f"WARNING: Source file not found: {abs_path} (Movie: {img.name})")
                continue

            if abs_path not in processed_files:
                utils.copy_file(abs_path, movies_dir)
                processed_files.add(abs_path)

            # Relink
            file_name = os.path.basename(abs_path)
            relative_path = f"//movies/{file_name}"
            if img.filepath != relative_path:
                img.filepath = relative_path
                count += 1

    print(f"Image localization complete. Relinked {count} items, copied {len(processed_files)} files.")
    return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_image_sequences(bpy.types.Operator):
    """Localize image sequences to //sequences folder"""
    bl_idname = "dy_pack_master.localize_image_sequences"
    bl_label = "Localize Image Sequences"
    bl_description = "Copy image sequence files to //sequences and relink"

    def execute(self, context):
        return localize_images(source_filter='SEQUENCE')

class DY_PACK_MASTER_OT_localize_movies(bpy.types.Operator):
    """Localize movie files to //movies folder"""
    bl_idname = "dy_pack_master.localize_movies"
    bl_label = "Localize Movies"
    bl_description = "Copy movie files to //movies and relink"

    def execute(self, context):
        return localize_images(source_filter='MOVIE')

class DY_PACK_MASTER_OT_localize_images(bpy.types.Operator):
    """Localize image sequences and movies to local folders"""
    bl_idname = "dy_pack_master.localize_images"
    bl_label = "Localize Images (Sequences & Movies)"
    bl_description = "Copy image sequences to //sequences and movies to //movies, then relink"

    def execute(self, context):
        return localize_images()

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_image_sequences)
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_movies)
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_images)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_images)
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_movies)
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_image_sequences)