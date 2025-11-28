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
