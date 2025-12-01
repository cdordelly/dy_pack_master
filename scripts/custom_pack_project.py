import bpy
import os
import platform
from datetime import datetime
from bpy_extras.io_utils import ExportHelper
from .modules import mesh_sequence_cache, vdb, references, render_settings, report, utils, images, movies, ocio, addons

# Get the addon package name for preferences lookup
ADDON_NAME = __package__.rsplit('.', 1)[0] if '.' in __package__ else __package__

class DY_PACK_MASTER_OT_custom_pack_project(bpy.types.Operator, ExportHelper):
    """Custom pack project with export dialog"""
    bl_idname = "dy_pack_master.custom_pack_project"
    bl_label = "Custom Pack Project"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper settings
    filename_ext = ".blend"
    filter_glob: bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})

    # --- UI Toggle Properties ---
    # Step 4: Localize Images (Sequences & Movies)
    localize_images: bpy.props.BoolProperty(
        name="Images (Sequences & Movies)",
        description="Copy image sequences and movies to local folders",
        default=True,
    )
    
    # Step 5: Localize Movie Clips
    localize_movie_clips: bpy.props.BoolProperty(
        name="Movie Clips",
        description="Copy movie clips (video editor) to local folder",
        default=True,
    )
    
    # Step 6: Localize Mesh Caches (ABC/USD)
    localize_mesh_caches: bpy.props.BoolProperty(
        name="Mesh Caches (ABC/USD)",
        description="Copy Alembic and USD cache files to local folder",
        default=True,
    )
    
    # Step 7: Localize References
    localize_references: bpy.props.BoolProperty(
        name="References",
        description="Copy linked .blend references to local folder",
        default=True,
    )
    
    # Step 8: Localize VDBs
    localize_vdbs: bpy.props.BoolProperty(
        name="VDBs",
        description="Copy VDB volume files to local folder",
        default=True,
    )
    
    # Extra: Localize OCIO
    localize_ocio: bpy.props.BoolProperty(
        name="OCIO Config File",
        description="Copy OCIO color configuration to local folder",
        default=False,
    )
    
    # Create parent directory
    create_parent_directory: bpy.props.BoolProperty(
        name="Create parent directory",
        description="Create a parent folder using the blend file name (e.g., my_file/my_file.blend)",
        default=True,
    )
    
    # Open directory after pack
    open_directory_after: bpy.props.BoolProperty(
        name="Open directory after pack",
        description="Open the output folder in file explorer after packing",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Localization options
        box = layout.box()
        box.label(text="Localize", icon='PACKAGE')
        col = box.column(align=True)
        col.prop(self, "localize_images")
        col.prop(self, "localize_movie_clips")
        col.prop(self, "localize_mesh_caches")
        col.prop(self, "localize_references")
        col.prop(self, "localize_vdbs")
        col.prop(self, "localize_ocio")
        
        # Localize Add-ons section
        box = layout.box()
        box.label(text="Localize Add-ons", icon='PREFERENCES')
        col = box.column()
        col.template_list(
            "DY_PACK_MASTER_UL_addons_list", "",
            scene, "dy_pack_master_addon_list",
            scene, "dy_pack_master_addon_index",
            rows=4
        )
        
        # Output options
        box = layout.box()
        box.label(text="Output Options", icon='FILE_FOLDER')
        col = box.column(align=True)
        col.prop(self, "create_parent_directory")
        col.prop(self, "open_directory_after")

    def invoke(self, context, event):
        # Check if blend file is saved
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Save blend file first!")
            return {'CANCELLED'}
        
        # Set default filename from current blend file
        current_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        self.filepath = current_name + ".blend"
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # Validate filepath
        if not self.filepath:
            self.report({'ERROR'}, "No output path specified")
            return {'CANCELLED'}
        
        # Store original filepath
        original_filepath = bpy.data.filepath
        
        # Determine output path
        output_dir = os.path.dirname(self.filepath)
        filename = os.path.basename(self.filepath)
        name, ext = os.path.splitext(filename)
        
        # Create parent directory if enabled
        if self.create_parent_directory:
            packed_dir = os.path.join(output_dir, name)
            new_filepath = os.path.join(packed_dir, filename)
        else:
            packed_dir = output_dir
            new_filepath = self.filepath
        
        # Create output directory
        utils.ensure_directory(packed_dir)
        
        # Log path
        log_path = os.path.join(packed_dir, "pack_log.txt")
        
        with utils.log_to_file(log_path):
            # Log header
            print("Pack Log - dy Pack Master (Custom Export)")
            print("=" * 50)
            print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"OS: {platform.system()} {platform.release()}")
            print(f"Blender: {bpy.app.version_string}")
            print(f"Source File: {original_filepath}")
            print(f"Pack Directory: {packed_dir}")
            print(f"OCIO Config: {os.environ.get('OCIO', 'Default (Blender built-in)')}")
            print("=" * 50)
            print()
            
            # Count enabled steps for progress
            total_steps = 5  # Fixed internal steps
            if self.localize_images:
                total_steps += 1
            if self.localize_movie_clips:
                total_steps += 1
            if self.localize_mesh_caches:
                total_steps += 1
            if self.localize_references:
                total_steps += 1
            if self.localize_vdbs:
                total_steps += 1
            if self.localize_ocio:
                total_steps += 1
            
            current_step = 0
            
            print("=" * 50)
            print("dy Pack Master - Custom Pack Project")
            print("=" * 50)
            
            # Step 0: Save current blend file
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Saving current blend file...")
            bpy.ops.wm.save_mainfile()
            
            # Step 1: Convert paths to absolute
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Converting asset paths to absolute...")
            utils.convert_all_paths_to_absolute()
            
            # Step 2: Save to pack directory
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Saving to pack directory...")
            try:
                bpy.ops.wm.save_as_mainfile(filepath=new_filepath, copy=False)
                print(f"  - Now working in: {new_filepath}")
            except Exception as e:
                print(f"ERROR: Failed to save file: {e}")
                return {'CANCELLED'}
            
            # Step 3: Pack blend file resources
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Packing blend file resources...")
            bpy.ops.file.pack_all()
            
            # Step 4: Localize Images (optional)
            if self.localize_images:
                current_step += 1
                print(f"\n[{current_step}/{total_steps}] Localizing Images (Sequences & Movies)...")
                images.localize_images(base_path=packed_dir)
            
            # Step 5: Localize Movie Clips (optional)
            if self.localize_movie_clips:
                current_step += 1
                print(f"\n[{current_step}/{total_steps}] Localizing Movie Clips...")
                movies.localize_movieclips(base_path=packed_dir)
            
            # Step 6: Localize Mesh Caches (optional)
            if self.localize_mesh_caches:
                current_step += 1
                print(f"\n[{current_step}/{total_steps}] Localizing Mesh Caches (ABC/USD)...")
                mesh_sequence_cache.localize_mesh_cache(base_path=packed_dir)
            
            # Step 7: Localize References (optional)
            if self.localize_references:
                current_step += 1
                print(f"\n[{current_step}/{total_steps}] Localizing References...")
                references.localize_references(base_path=packed_dir)
            
            # Step 8: Localize VDBs (optional)
            if self.localize_vdbs:
                current_step += 1
                print(f"\n[{current_step}/{total_steps}] Localizing VDBs...")
                vdb.localize_vdb(base_path=packed_dir)
            
            # Extra: Localize OCIO (optional)
            if self.localize_ocio:
                current_step += 1
                print(f"\n[{current_step}/{total_steps}] Localizing OCIO...")
                ocio.localize_ocio()

            # Localize Add-ons (based on selection in list)
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Localizing Add-ons...")
            addons.localize_addons(base_path=packed_dir)
            
            # Step 9: Set relative output path
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Setting relative output path...")
            render_settings.set_relative_output()
            
            # Step 10: Generate missing files report
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Generating missing files report...")
            report.missing_files_report(base_path=packed_dir)
            
            # Step 11: Save final packed blend file
            current_step += 1
            print(f"\n[{current_step}/{total_steps}] Saving final packed blend file...")
            bpy.ops.wm.save_mainfile()
            
            print("\n" + "=" * 50)
            print("Custom Pack Project Complete!")
            print(f"Packed project: {new_filepath}")
            print("=" * 50)
        
        # Open directory after pack if enabled
        if self.open_directory_after:
            utils.open_directory(packed_dir)

        # Optionally reopen original file based on preferences
        prefs = context.preferences.addons.get(ADDON_NAME)
        if prefs and prefs.preferences.reopen_original_file:
            print(f"\nReopening original file: {original_filepath}")
            bpy.ops.wm.open_mainfile(filepath=original_filepath)
        
        self.report({'INFO'}, f"Project packed: {new_filepath}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(DY_PACK_MASTER_OT_custom_pack_project)

def unregister():
    bpy.utils.unregister_class(DY_PACK_MASTER_OT_custom_pack_project)