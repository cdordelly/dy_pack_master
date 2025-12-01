bl_info = {
    "name": "dy Pack Master",
    "author": "Carlos Dordelly - @cdordelly",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > UI > dy Pack Master",
    "description": "Make Blender project files portable for render farms by localizing assets, addons, and dependencies.",
    "warning": "",
    "doc_url": "https://github.com/cdordelly/dy_pack_master",
    "category": "System",
}

import bpy
from .scripts import ui
from .scripts import modules
from .scripts import pack_project
from .scripts import custom_pack_project

# Force UI refresh by toggling region redraw
def update_menu_location(self, context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'UI':
                        region.tag_redraw()

# Addon Preferences
class DY_PACK_MASTER_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    menu_location: bpy.props.EnumProperty(
        name="Menu Location",
        description="Where to show the dy Pack Master menu",
        items=[
            ('EXPORT', "File > Export", "Show in File > Export menu"),
            ('SIDEBAR', "3D Viewport Sidebar", "Show in 3D Viewport N-Panel"),
        ],
        default='SIDEBAR',
        update=update_menu_location,  # Trigger UI refresh on change
    )
    
    blend_suffix: bpy.props.StringProperty(
        name="Blend File Suffix",
        description="Suffix to add when saving packed blend file",
        default="_packed",
    )

    reopen_original_file: bpy.props.BoolProperty(
        name="Reopen original file after pack",
        description="Reopen the original blend file after packing",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="UI Settings", icon='PREFERENCES')
        layout.prop(self, "menu_location")
        layout.separator()
        layout.label(text="Packing Settings", icon='FILE_BLEND')
        layout.prop(self, "blend_suffix")
        layout.prop(self, "reopen_original_file")

def register():
    bpy.utils.register_class(DY_PACK_MASTER_Preferences)
    modules.register()
    pack_project.register()
    custom_pack_project.register()
    ui.register()

def unregister():
    ui.unregister()
    custom_pack_project.unregister()
    pack_project.unregister()
    modules.unregister()
    bpy.utils.unregister_class(DY_PACK_MASTER_Preferences)