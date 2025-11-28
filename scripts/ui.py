import bpy

# Get the addon package name for preferences lookup
# For extensions: __package__ is 'bl_ext.user_default.dy_pack_master.scripts'
# We need 'bl_ext.user_default.dy_pack_master'
ADDON_NAME = __package__.rsplit('.', 1)[0] if '.' in __package__ else __package__

class DY_PACK_MASTER_PT_main(bpy.types.Panel):
    """Creates a Panel in the 3D View N-Panel"""
    bl_label = "dy Pack Master"
    bl_idname = "DY_PACK_MASTER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "dy Pack Master"

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons.get(ADDON_NAME)
        if prefs:
            return prefs.preferences.menu_location == 'SIDEBAR'
        return False

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Export", icon='PACKAGE')
        row = layout.row()
        row.scale_y = 2.0
        row.operator("dy_pack_master.pack_project", icon='EXPORT')
        
        layout.separator()
        
        layout.label(text="Tools", icon='TOOL_SETTINGS')
        layout.operator("dy_pack_master.addons_tool", icon='PREFERENCES', text="Localize Add-ons")
        layout.operator("dy_pack_master.localize_ocio", icon='COLOR', text="Localize OCIO")
        layout.operator("dy_pack_master.missing_files_report", icon='ERROR', text="Missing Files Report")

def menu_func_export(self, context):
    prefs = context.preferences.addons.get(ADDON_NAME)
    if prefs and prefs.preferences.menu_location == 'SIDEBAR':
        return
    
    layout = self.layout
    layout.separator()
    layout.label(text="dy Pack Master", icon='PACKAGE')
    layout.operator("dy_pack_master.pack_project", text="Pack Project", icon='EXPORT')
    layout.operator("dy_pack_master.addons_tool", text="Localize Add-ons", icon='PREFERENCES')
    layout.operator("dy_pack_master.localize_ocio", text="Localize OCIO", icon='COLOR')
    layout.operator("dy_pack_master.missing_files_report", text="Missing Files Report", icon='ERROR')

classes = (
    DY_PACK_MASTER_PT_main,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    if hasattr(bpy.types, 'TOPBAR_MT_file_export'):
        try:
            bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        except:
            pass
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)