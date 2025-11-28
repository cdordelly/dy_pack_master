import bpy

# Get the addon package name for preferences lookup
ADDON_NAME = __package__.rsplit('.', 1)[0] if '.' in __package__ else __package__

# -------------------------------------------------------------------------
# Main Panel (3D Viewport Sidebar)
# -------------------------------------------------------------------------
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
        scene = context.scene
        
        # --- Export Section ---
        box = layout.box()
        box.label(text="Export", icon='PACKAGE')
        row = box.row()
        row.scale_y = 2.0
        row.operator("dy_pack_master.pack_project", icon='EXPORT')
        
        # --- Localize Add-ons Section (Collapsible Box) ---
        box = layout.box()
        row = box.row(align=True)
        row.prop(
            scene, "dy_pack_master_expand_addons",
            icon='DOWNARROW_HLT' if scene.dy_pack_master_expand_addons else 'RIGHTARROW',
            icon_only=True, emboss=False
        )
        row.label(text="Localize Add-ons", icon='PREFERENCES')
        
        if scene.dy_pack_master_expand_addons:
            col = box.column()
            col.template_list(
                "DY_PACK_MASTER_UL_addons_list", "",
                scene, "dy_pack_master_addon_list",
                scene, "dy_pack_master_addon_index",
                rows=6
            )
            row = col.row(align=True)
            row.operator("dy_pack_master.localize_addons", icon='EXPORT', text="Localize Selected")
            row.operator("dy_pack_master.refresh_addons", icon='FILE_REFRESH', text="")
        
        # --- Tools Section (Collapsible Box) ---
        box = layout.box()
        row = box.row(align=True)
        row.prop(
            scene, "dy_pack_master_expand_tools",
            icon='DOWNARROW_HLT' if scene.dy_pack_master_expand_tools else 'RIGHTARROW',
            icon_only=True, emboss=False
        )
        row.label(text="Tools", icon='TOOL_SETTINGS')
        
        if scene.dy_pack_master_expand_tools:
            col = box.column(align=True)
            col.operator("dy_pack_master.localize_ocio", icon='COLOR', text="Localize OCIO")
            col.operator("dy_pack_master.missing_files_report", icon='ERROR', text="Missing Files Report")

# -------------------------------------------------------------------------
# File > Export Menu Function
# -------------------------------------------------------------------------
def menu_func_export(self, context):
    prefs = context.preferences.addons.get(ADDON_NAME)
    if prefs and prefs.preferences.menu_location == 'SIDEBAR':
        return
    
    layout = self.layout
    layout.separator()
    layout.label(text="dy Pack Master", icon='PACKAGE')
    layout.operator("dy_pack_master.pack_project", text="Pack Project", icon='EXPORT')
    # File > Export uses the popup dialog version
    layout.operator("dy_pack_master.addons_tool", text="Localize Add-ons", icon='PREFERENCES')
    layout.operator("dy_pack_master.localize_ocio", text="Localize OCIO", icon='COLOR')
    layout.operator("dy_pack_master.missing_files_report", text="Missing Files Report", icon='ERROR')

# -------------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------------
classes = (
    DY_PACK_MASTER_PT_main,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    # Register expand/collapse properties
    bpy.types.Scene.dy_pack_master_expand_addons = bpy.props.BoolProperty(
        name="Expand Addons", default=False
    )
    bpy.types.Scene.dy_pack_master_expand_tools = bpy.props.BoolProperty(
        name="Expand Tools", default=False
    )

def unregister():
    # Cleanup expand properties
    if hasattr(bpy.types.Scene, 'dy_pack_master_expand_addons'):
        del bpy.types.Scene.dy_pack_master_expand_addons
    if hasattr(bpy.types.Scene, 'dy_pack_master_expand_tools'):
        del bpy.types.Scene.dy_pack_master_expand_tools
    
    if hasattr(bpy.types, 'TOPBAR_MT_file_export'):
        try:
            bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        except:
            pass
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)