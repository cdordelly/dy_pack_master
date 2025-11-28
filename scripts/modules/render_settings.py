import bpy
import os

def set_relative_output():
    """
    Sets the render output path to a relative path '//render/' while preserving 
    the current output filename/prefix.
    """
    scene = bpy.context.scene
    current_path = scene.render.filepath
    
    if not current_path:
        filename = "render_"
    else:
        current_path = os.path.normpath(current_path)
        filename = os.path.basename(current_path)
        
    new_path = f"//render/{filename}"
    
    if scene.render.filepath != new_path:
        scene.render.filepath = new_path
        return True, new_path
    return False, new_path

class DY_PACK_MASTER_OT_rel_output_path(bpy.types.Operator):
    """Set Relative Output Path"""
    bl_idname = "dy_pack_master.rel_output_path"
    bl_label = "Set Relative Output"
    bl_description = "Set render output to //render/filename"

    def execute(self, context):
        changed, path = set_relative_output()
        if changed:
            self.report({'INFO'}, f"Output path set to: {path}")
        else:
            self.report({'INFO'}, f"Output path already relative: {path}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_rel_output_path)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_rel_output_path)
