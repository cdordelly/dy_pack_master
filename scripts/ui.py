import bpy

class DY_PACK_MASTER_PT_main(bpy.types.Panel):
    """Creates a Panel in the 3D View N-Panel"""
    bl_label = "dy Pack Master"
    bl_idname = "DY_PACK_MASTER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "dy Pack Master"

    @classmethod
    def poll(cls, context):
        # Only show panel if menu_location preference is set to SIDEBAR
        prefs = context.preferences.addons.get('dy_pack_master')
        if prefs:
            return prefs.preferences.menu_location == 'SIDEBAR'
        return False  # Hide by default (default is EXPORT menu)

    def draw(self, context):
        layout = self.layout
        
        # Main Pack Button (Big and prominent)
        layout.label(text="Export", icon='PACKAGE')
        row = layout.row()
        row.scale_y = 2.0  # Make it bigger
        row.operator("dy_pack_master.pack_project", icon='EXPORT')
        
        layout.separator()
        
        # Individual Tools
        layout.label(text="Tools", icon='TOOL_SETTINGS')
        layout.operator("dy_pack_master.addons_tool", icon='PREFERENCES', text="Localize Add-ons")
        layout.operator("dy_pack_master.localize_ocio", icon='COLOR', text="Localize OCIO")
        layout.operator("dy_pack_master.missing_files_report", icon='ERROR', text="Missing Files Report")

def menu_func_export(self, context):
    # Only show in export menu if preference is set to EXPORT
    prefs = context.preferences.addons.get('dy_pack_master')
    if prefs and prefs.preferences.menu_location == 'SIDEBAR':
        return  # Don't show if using sidebar
    
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
    
    # Always register to export menu (visibility controlled by menu_func_export)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    # Unregister from export menu
    if hasattr(bpy.types, 'TOPBAR_MT_file_export'):
        try:
            bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        except:
            pass
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
