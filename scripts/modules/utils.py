import bpy
import os
import shutil

def get_absolute_path(path):
    """Convert a Blender path (//) to an absolute path."""
    return os.path.abspath(bpy.path.abspath(path))

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
        # Check if it's the same file to avoid redundant copy
        # For now, simple existence check is enough as per requirements
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

def save_blend_with_suffix(suffix):
    """
    Saves the current blend file with a suffix added to the filename.
    Example: scene.blend -> scene_collect.blend
    """
    current_filepath = bpy.data.filepath
    
    if not current_filepath:
        print("ERROR: Blend file must be saved first before using 'Save As' with suffix.")
        return
    
    # Split the path into directory, name, and extension
    directory = os.path.dirname(current_filepath)
    filename = os.path.basename(current_filepath)
    name, ext = os.path.splitext(filename)
    
    # Create new filename with suffix
    new_filename = f"{name}{suffix}{ext}"
    new_filepath = os.path.join(directory, new_filename)
    
    # Save the file
    try:
        bpy.ops.wm.save_as_mainfile(filepath=new_filepath, copy=False)
        print(f"File saved as: {new_filepath}")
        return new_filepath
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")