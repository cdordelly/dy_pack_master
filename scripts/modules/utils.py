import bpy
import os
import shutil

def get_absolute_path(path):
    """Convert a Blender path (//) to an absolute path with forward slashes."""
    return os.path.abspath(bpy.path.abspath(path)).replace('\\', '/')

def convert_all_paths_to_absolute():
    """Convert all asset paths to absolute before saving to new location."""
    from . import mesh_sequence_cache, vdb, references
    
    print("  - Converting mesh cache paths...")
    mesh_sequence_cache.set_absolute_path_mesh_cache()
    
    print("  - Converting VDB paths...")
    vdb.set_absolute_path_vdb()
    
    print("  - Converting reference paths...")
    references.set_absolute_path_references()
    
    print("  - Converting image paths...")
    for img in bpy.data.images:
        if img.source in {'FILE', 'SEQUENCE'} and not img.packed_file and img.filepath:
            abs_path = get_absolute_path(img.filepath)
            if img.filepath != abs_path:
                img.filepath = abs_path

def ensure_directory(path):
    """Ensure a directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def copy_file(src, dest_dir, overwrite=False):
    """Copy a file to a destination directory."""
    if not os.path.exists(src):
        print(f"Source file not found: {src}")
        return None
    
    filename = os.path.basename(src)
    dest_path = os.path.join(dest_dir, filename)
    
    if os.path.exists(dest_path) and not overwrite:
        return dest_path
        
    try:
        shutil.copy2(src, dest_path)
        return dest_path
    except Exception as e:
        print(f"Error copying {src} to {dest_path}: {e}")
        return None

def get_blend_dir():
    """Get the directory of the current blend file."""
    if not bpy.data.filepath:
        return None
    return os.path.dirname(bpy.data.filepath)

def save_blend_with_suffix(suffix, copy=True):
    """Save current blend file with a suffix. Example: scene.blend -> scene_packed.blend"""
    current_filepath = bpy.data.filepath
    if not current_filepath:
        print("ERROR: Blend file must be saved first.")
        return None
    
    directory = os.path.dirname(current_filepath)
    filename = os.path.basename(current_filepath)
    name, ext = os.path.splitext(filename)
    
    new_filename = f"{name}{suffix}{ext}"
    new_filepath = os.path.join(directory, new_filename)
    
    try:
        bpy.ops.wm.save_as_mainfile(filepath=new_filepath, copy=copy)
        print(f"File saved as: {new_filepath}")
        return new_filepath
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return None

def save_blend_to_pack_directory(suffix, copy=True):
    """
    Create a pack directory and save blend file there.
    Example: "scn010.blend" -> "scn010_packed/scn010_packed.blend"
    """
    current_filepath = bpy.data.filepath
    if not current_filepath:
        print("ERROR: Blend file must be saved first.")
        return None
    
    directory = os.path.dirname(current_filepath)
    filename = os.path.basename(current_filepath)
    name, ext = os.path.splitext(filename)
    
    packed_name = f"{name}{suffix}"
    packed_dir = os.path.join(directory, packed_name)
    new_filepath = os.path.join(packed_dir, f"{packed_name}{ext}")
    
    ensure_directory(packed_dir)
    print(f"  - Created directory: {packed_dir}")
    
    try:
        bpy.ops.wm.save_as_mainfile(filepath=new_filepath, copy=copy)
        print(f"  - Blend file saved to: {new_filepath}")
        return new_filepath
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return None