import bpy
import addon_utils
import os
import zipfile
from bpy.app.handlers import persistent
from . import utils

def load_blacklist():
    """Load the addon blacklist from external txt file."""
    blacklist_path = os.path.join(os.path.dirname(__file__), "addons_blacklist.txt")
    blacklist = set()
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    blacklist.add(line)
    return blacklist

def is_blacklisted(module_name, blacklist):
    """Check if a module name is in the blacklist.
    
    Handles full extension paths like 'bl_ext.user_default.dy_pack_master'
    by also checking the last component of the module name.
    """
    if module_name in blacklist:
        return True
    # Check if the last part of the module name (after last dot) is blacklisted
    # This handles bl_ext.blender_org.animall -> animall
    short_name = module_name.rsplit('.', 1)[-1]
    return short_name in blacklist

def populate_addon_list(scene):
    """Populates the scene.dy_pack_master_addon_list with enabled addons"""
    scene.dy_pack_master_addon_list.clear()
    
    # Reload blacklist from file on each refresh
    blacklist = load_blacklist()

    for mod in addon_utils.modules():
        name = mod.__name__
        is_enabled, _ = addon_utils.check(name)
        if not is_enabled: continue
        if is_blacklisted(name, blacklist): continue
            
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

def localize_addons(base_path=None):
    """Copy selected add-ons to the local 'addons' folder."""
    base_path = base_path or utils.get_blend_dir()
    if not base_path:
        print("ERROR: Blend file must be saved before localizing add-ons.")
        return {'CANCELLED'}

    local_addons_dir = os.path.join(base_path, "addons")
    utils.ensure_directory(local_addons_dir)

    count = 0
    scene = bpy.context.scene
    for item in scene.dy_pack_master_addon_list:
        if item.selected:
            _localize_addon_item(item, local_addons_dir)
            count += 1
    
    if count == 0:
        print("No add-ons selected to localize.")
    else:
        print(f"Add-on localization complete. Localized {count} add-ons.")
    return {'FINISHED'}

def _localize_addon_item(item, dest_dir):
    """Helper to localize a single addon item."""
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
            print(f"  - Zipped package: {module_name} -> {zip_path}")
        except Exception as e:
            print(f"ERROR zipping {module_name}: {e}")
    else:
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                arcname = os.path.basename(src_path)
                zipf.write(src_path, arcname)
            print(f"  - Zipped file: {module_name} -> {zip_path}")
        except Exception as e:
            print(f"ERROR zipping {module_name}: {e}")

@persistent
def load_handler(dummy):
    bpy.app.timers.register(lambda: populate_addon_list(bpy.context.scene) or None, first_interval=0.1)

class DY_PACK_MASTER_Item(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    module_name: bpy.props.StringProperty(name="Module Name")
    path: bpy.props.StringProperty(name="Path")
    description: bpy.props.StringProperty(name="Description")
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
    bl_label = "Localize Selected"

    def execute(self, context):
        if not utils.get_blend_dir():
            self.report({'ERROR'}, "Save blend file first!")
            return {'CANCELLED'}

        result = localize_addons()
        if result == {'FINISHED'}:
            count = sum(1 for item in context.scene.dy_pack_master_addon_list if item.selected)
            self.report({'INFO'}, f"Localized {count} add-ons.")
        return result

class DY_PACK_MASTER_UL_addons_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "selected", text="")
        row.label(text=item.name)
        row.label(text=f"({item.module_name})", icon='SCRIPT')

class DY_PACK_MASTER_OT_addons_tool(bpy.types.Operator):
    """Open the Addon Localization Tool."""
    bl_idname = "dy_pack_master.addons_tool"
    bl_label = "Localize Add-ons"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Save blend file first!")
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.template_list("DY_PACK_MASTER_UL_addons_list", "", scene, "dy_pack_master_addon_list", scene, "dy_pack_master_addon_index", rows=10)
    
    def execute(self, context):
        result = bpy.ops.dy_pack_master.localize_addons()
        return result

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