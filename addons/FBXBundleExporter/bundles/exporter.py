import os
import pathlib 

import bpy
from .. import platforms

prefix_copy = "__EXPORT_PREFIX_"

def copy_object(obj, convert = True):
    name_original = obj.name
    obj.name = prefix_copy+name_original

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.hide_viewport = False
    #bpy.context.view_layer.update()
    
    # Copy
    bpy.ops.object.duplicate()
    if convert:
        bpy.ops.object.convert(target='MESH')
    bpy.context.object.name = name_original

    return bpy.context.object

def export(bundles, path, target_platform):
        # Store previous settings
        previous_selection = bpy.context.selected_objects.copy()
        previous_active = bpy.context.view_layer.objects.active
        previous_unit_system = bpy.context.scene.unit_settings.system
        previous_pivot = bpy.context.scene.tool_settings.transform_pivot_point
        previous_cursor = bpy.context.scene.cursor.location

        if not bpy.context.view_layer.objects.active:
            bpy.context.view_layer.objects.active = None

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.unit_settings.system = 'METRIC'	
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

        for bundle in bundles:
            modifiers = bundle.modifiers
            print(modifiers)
            name = bundle.key
            meshes = bundle.meshes
            helpers = bundle.helpers
            armatures = bundle.armatures
            all_data = bundle.objects

            pivot = bundle.pivot

            export_meshes = []

            for obj in meshes:
                export_meshes.append(copy_object(obj))

            export_helpers = []
            for helper in helpers:
                copied_helper = copy_object(helper, convert = False)
                copied_helper.scale[0]*= 0.01
                copied_helper.scale[1]*= 0.01
                copied_helper.scale[2]*= 0.01
                export_helpers.append(copied_helper)

            export_armatures = []

            bpy.ops.object.select_all(action="DESELECT")

            # Apply modifiers

            # full = self.process_path(name, path)+"{}".format(os.path.sep)+platforms.platforms[mode].get_filename( self.process_name(name) )  		
            # os.path.join(folder, name)+"."+platforms.platforms[mode].extension
            path_folder = path
            path_name = name
            for modifier in bundle.modifiers:
                export_meshes, export_helpers, export_armatures = modifier.process_objects(name, export_meshes, export_helpers, export_armatures)
                pivot = modifier.process_pivot(pivot, export_meshes, export_helpers, export_armatures)
                path_folder = modifier.process_path(path_name, path_folder)
                path_name = modifier.process_name(path_name)

            for x in export_meshes + export_helpers + export_armatures:
                x.location-= pivot

            print(export_meshes)
            print(export_helpers)
            print(export_armatures)

            path_full = os.path.join(path_folder, path_name)+"."+platforms.platforms[target_platform].extension
            
            # Create path if not yet available
            directory = os.path.dirname(path_full)
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

            # Select all export objects
            bpy.ops.object.select_all(action="DESELECT")
            for obj in export_meshes + export_helpers + export_armatures:
                obj.select_set(True)

            # Export per platform (Unreal, Unity, ...)
            print("Export {}x = {}".format(len(meshes),path_full))
            platforms.platforms[target_platform].file_export(path_full)

            # Delete export_meshes
            bpy.ops.object.delete()
            export_meshes.clear()
            
            # Restore names
            for obj in all_data:
                obj.name = obj.name.replace(prefix_copy,"")

        # Restore previous settings
        bpy.context.scene.unit_settings.system = previous_unit_system
        bpy.context.scene.tool_settings.transform_pivot_point = previous_pivot
        bpy.context.scene.cursor.location = previous_cursor
        bpy.context.view_layer.objects.active = previous_active
        bpy.ops.object.select_all(action='DESELECT')
        for obj in previous_selection:
            obj.select_set(True)

        # Show popup
        
        def draw(self, context):
            filenames = []
            # Get bundle file names
            for bundle in bundles:
                name = bundle.key
                for modifier in bundle.modifiers:
                    name = modifier.process_name(name)	
                filenames.append(name+"."+platforms.platforms[target_platform].extension)

            self.layout.label(text="Exported:")
            for x in filenames:
                self.layout.label(text=x)

            self.layout.operator("wm.path_open", text=path, icon='FILE_FOLDER').filepath = path

        bpy.context.window_manager.popup_menu(draw, title = "Exported {}x files".format(len(bundles)), icon = 'INFO')
        