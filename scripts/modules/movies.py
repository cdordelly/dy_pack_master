import bpy
import os
from . import utils

def set_absolute_path_movieclips():
    """Converts the filepath of all movie clips to an absolute path."""
    clips_to_process = []
    for clip in bpy.data.movieclips:
        if not clip.filepath:
            continue
            
        abs_path = utils.get_absolute_path(clip.filepath)
        if clip.filepath != abs_path:
            clip.filepath = abs_path
            
        clips_to_process.append(clip)
    
    return clips_to_process

def localize_movieclips(base_path=None):
    """Copies movie clip files to local 'movies' folder and relinks them relatively."""
    base_path = base_path or utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing movie clips.")
        return {'CANCELLED'}

    # Check if there are any movie clips with filepaths to process
    clips_to_process = []
    for clip in bpy.data.movieclips:
        if not clip.filepath:
            continue
        # Skip already localized clips
        normalized_path = clip.filepath.replace('\\', '/')
        if normalized_path.startswith("//movies"):
            continue
        clips_to_process.append(clip)
    
    # Early exit if no movie clips to localize
    if not clips_to_process:
        print("No movie clips found to localize.")
        return {'FINISHED'}

    # Only create directory if we have clips to process
    movies_dir = os.path.join(base_path, "movies")
    utils.ensure_directory(movies_dir)
    
    processed_files = set()
    count = 0

    for clip in clips_to_process:
        abs_path = utils.get_absolute_path(clip.filepath)
        abs_path = os.path.normpath(abs_path)
        
        if not os.path.exists(abs_path):
            print(f"WARNING: Source file not found: {abs_path} (Clip: {clip.name})")
            continue

        if abs_path not in processed_files:
            utils.copy_file(abs_path, movies_dir)
            processed_files.add(abs_path)

        # Relink
        file_name = os.path.basename(abs_path)
        relative_path = f"//movies/{file_name}"
        if clip.filepath != relative_path:
            clip.filepath = relative_path
            count += 1

    print(f"Movie clip localization complete. Relinked {count} clips.")
    return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_movieclips(bpy.types.Operator):
    """Localize movie clip files to //movies folder"""
    bl_idname = "dy_pack_master.localize_movieclips"
    bl_label = "Localize Movie Clips"
    bl_description = "Copy movie clip files to //movies and relink"

    def execute(self, context):
        return localize_movieclips()

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_localize_movieclips)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_localize_movieclips)