import bpy

class DY_PACK_MASTER_PT_main(bpy.types.Panel):
    """Creates a Panel in the 3D View N-Panel"""
    bl_label = "dy Pack Master"
    bl_idname = "DY_PACK_MASTER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "dy Pack Master"

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

class DY_PACK_MASTER_MT_menu(bpy.types.Menu):
    bl_label = "dy Pack Master"
    bl_idname = "DY_PACK_MASTER_MT_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("dy_pack_master.pack_project", text="Pack Project", icon='EXPORT')
        layout.separator()
        layout.operator("dy_pack_master.addons_tool", text="Localize Add-ons Tool", icon='PREFERENCES')
        layout.operator("dy_pack_master.localize_ocio", text="Localize OCIO", icon='COLOR')
        layout.operator("dy_pack_master.missing_files_report", text="Missing Files Report", icon='ERROR')

def menu_func(self, context):
    self.layout.separator()
    self.layout.menu(DY_PACK_MASTER_MT_menu.bl_idname, icon='PACKAGE')

classes = (
    DY_PACK_MASTER_PT_main,
    DY_PACK_MASTER_MT_menu,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
