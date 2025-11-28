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
        
        # General Tools
        layout.label(text="General Tools", icon='TOOL_SETTINGS')
        layout.operator("dy_pack_master.rel_output_path", icon='RENDER_RESULT')
        layout.operator("dy_pack_master.missing_files_report", icon='ERROR')
        
        layout.separator()
        
        # Asset Localization
        layout.label(text="Asset Localization", icon='FILE_3D')
        layout.operator("dy_pack_master.localize_abc", icon='FILE_CACHE')
        layout.operator("dy_pack_master.localize_vdb", icon='FILE_VOLUME')
        layout.operator("dy_pack_master.localize_references", icon='LINK_BLEND')
        layout.operator("dy_pack_master.localize_ocio", icon='COLOR')
        
        layout.separator()
        
        # Addons
        layout.label(text="Addons", icon='PREFERENCES')
        layout.operator("dy_pack_master.addons_tool", icon='WINDOW')

class DY_PACK_MASTER_MT_menu(bpy.types.Menu):
    bl_label = "dy Pack Master"
    bl_idname = "DY_PACK_MASTER_MT_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("dy_pack_master.addons_tool", text="Localize Addons Tool", icon='PREFERENCES')
        layout.separator()
        layout.operator("dy_pack_master.localize_abc", text="Localize Alembics")
        layout.operator("dy_pack_master.localize_vdb", text="Localize VDBs")
        layout.operator("dy_pack_master.localize_references", text="Localize References")
        layout.operator("dy_pack_master.localize_ocio", text="Localize OCIO")
        layout.separator()
        layout.operator("dy_pack_master.rel_output_path", text="Set Relative Output")
        layout.operator("dy_pack_master.missing_files_report", text="Missing Files Report")

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
    bpy.types.TOPBAR_MT_file.append(menu_func)

def unregister():
    bpy.types.TOPBAR_MT_file.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
