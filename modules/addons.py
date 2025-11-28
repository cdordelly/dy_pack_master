import bpy
import addon_utils
import os
import zipfile
from bpy.app.handlers import persistent
from .. import utils

BLACKLIST = {
    "cycles",
    "pose_library",
    "io_scene_obj",
    "io_scene_fbx",
    "io_scene_gltf2",
    "io_mesh_uv_layout",
    "io_curve_svg",
    "io_mesh_ply",
    "io_mesh_stl",
    "io_scene_x3d",
    "space_view3d_spacebar_menu",
    "viewport_vr_preview",
    "bl_ext.user_default",
    "io_anim_bvh",
    "bl_pkg",
    "dy_pack_master" # Don't pack yourself!
}

def populate_addon_list(scene):
    """Populates the scene.dy_pack_master_addon_list with enabled addons"""
    scene.dy_pack_master_addon_list.clear()

    for mod in addon_utils.modules():
        name = mod.__name__
        is_enabled, _ = addon_utils.check(name)
        if not is_enabled: continue
        if name in BLACKLIST: continue
            
        info = addon_utils.module_bl_info(mod)
        addon_title = info.get("name", name)
        addon_path = getattr(mod, '__file__', '')
        
        if not addon_path: continue

        item = scene.dy_pack_master_addon_list.add()
        item.name = addon_title
        item.module_name = name
        item.path = addon_path
        item.selected = False
    
    print(f"Refreshed add-on list: {len(scene.dy_pack_master_addon_list)} items found.")

@persistent
def load_handler(dummy):
    bpy.app.timers.register(lambda: populate_addon_list(bpy.context.scene) or None, first_interval=0.1)

class DY_PACK_MASTER_Item(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    path: bpy.props.StringProperty(name="Path")
    selected: bpy.props.BoolProperty(name="Selected", default=False)

class DY_PACK_MASTER_OT_refresh_addons(bpy.types.Operator):
    """Refresh the list of enabled add-ons"""
    bl_idname = "dy_pack_master.refresh_addons"
    bl_label = "Refresh Add-ons List"

    def execute(self, context):
        populate_addon_list(context.scene)
        return {'FINISHED'}

class DY_PACK_MASTER_OT_localize_addons(bpy.types.Operator):
    """Copy selected add-ons to the local 'addons' folder"""
    bl_idname = "dy_pack_master.localize_addons"
    bl_label = "Localize Selected Add-ons"

    def execute(self, context):
        base_path = utils.get_blend_dir()
        if not base_path:
            self.report({'ERROR'}, "Save blend file first!")
            return {'CANCELLED'}

        local_addons_dir = os.path.join(base_path, "addons")
        utils.ensure_directory(local_addons_dir)

        count = 0
        scene = context.scene
        for item in scene.dy_pack_master_addon_list:
            if item.selected:
                self.localize_addon(item, local_addons_dir)
                count += 1
        
        self.report({'INFO'}, f"Localized {count} add-ons.")
        return {'FINISHED'}

    def localize_addon(self, item, dest_dir):
        src_path = item.path
        module_name = item.module_name
        clean_name = module_name.split('.')[-1]
        zip_path = os.path.join(dest_dir, f"{clean_name}.zip")
        
        if os.path.basename(src_path) == '__init__.py':
            src_folder = os.path.dirname(src_path)
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(src_folder):
                        dirs[:] = [d for d in dirs if d != '__pycache__']
                        for file in files:
                            if file == '__pycache__' or file.endswith('.pyc'): continue
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, src_folder)
                            arcname = os.path.join(clean_name, rel_path)
                            zipf.write(file_path, arcname)
                print(f"Zipped package: {module_name} -> {zip_path}")
            except Exception as e:
                print(f"ERROR zipping {module_name}: {e}")
        else:
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    arcname = os.path.basename(src_path)
                    zipf.write(src_path, arcname)
                print(f"Zipped file: {module_name} -> {zip_path}")
            except Exception as e:
                print(f"ERROR zipping {module_name}: {e}")

class DY_PACK_MASTER_UL_addons_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "selected", text="")
        row.label(text=item.name)
        row.label(text=f"({item.module_name})", icon='SCRIPT')

class DY_PACK_MASTER_OT_addons_tool(bpy.types.Operator):
    """Open the Addon Localization Tool in a floating dialog"""
    bl_idname = "dy_pack_master.addons_tool"
    bl_label = "Localize Add-ons Tool"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Select Add-ons to Localize", icon='PREFERENCES')
        
        row = layout.row()
        row.template_list("DY_PACK_MASTER_UL_addons_list", "", scene, "dy_pack_master_addon_list", scene, "dy_pack_master_addon_index", rows=10)
        
        row = layout.row()
        row.operator("dy_pack_master.localize_addons", icon='EXPORT')
        
        row = layout.row()
        row.operator("dy_pack_master.refresh_addons", icon='FILE_REFRESH')
    
    def execute(self, context):
        return {'FINISHED'}

classes = (
    DY_PACK_MASTER_Item,
    DY_PACK_MASTER_OT_refresh_addons,
    DY_PACK_MASTER_OT_localize_addons,
    DY_PACK_MASTER_OT_addons_tool,
    DY_PACK_MASTER_UL_addons_list,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.dy_pack_master_addon_list = bpy.props.CollectionProperty(type=DY_PACK_MASTER_Item)
    bpy.types.Scene.dy_pack_master_addon_index = bpy.props.IntProperty()
    
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)
        
    try:
        if bpy.context.scene:
            populate_addon_list(bpy.context.scene)
    except:
        pass

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.dy_pack_master_addon_list
    del bpy.types.Scene.dy_pack_master_addon_index
    
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
