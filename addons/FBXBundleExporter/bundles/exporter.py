import os
import pathlib 

import bpy
from .. import platforms

from ..settings import prefix_copy, mesh_types, empty_types, armature_types

def copy_objects(objects):

    bpy.ops.object.select_all(action="DESELECT")

    export_collection = bpy.data.collections.new('armature_join_temp_collection')
    bpy.context.scene.collection.children.link(export_collection)

    for obj in objects:
        obj['__orig_name__'] = obj.name
        obj['__orig_hide__'] = obj.hide_viewport
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        obj.hide_viewport = False
        obj.name = prefix_copy + obj.name
        #traverse tree and unhide all collections too

    bpy.ops.object.duplicate()

    copied_objects = [x for x in bpy.context.scene.objects if x.select_get()]

    for obj in copied_objects:
        obj.name = obj['__orig_name__']

    meshes = [x for x in copied_objects if x.type in mesh_types]
    helpers = [x for x in copied_objects if x.type in empty_types]
    armatures = [x for x in copied_objects if x.type in armature_types]

    return meshes, helpers, armatures

def restore_defaults(objects):
    for obj in objects:
        obj.name = obj['__orig_name__']
        obj.hide_viewport = obj['__orig_hide__']

        del obj['__orig_name__']
        del obj['__orig_hide__']
    

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

        #bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.unit_settings.system = 'METRIC'	
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

        for bundle in bundles:
            modifiers = bundle.modifiers
            print(modifiers)
            name = bundle.key
            #meshes = bundle.meshes
            #helpers = bundle.helpers
            #armatures = bundle.armatures
            all_data = bundle.objects
            pivot = bundle.pivot

            export_meshes, export_helpers, export_armatures = copy_objects(all_data)

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

            path_folder = bpy.path.abspath(path_folder)
            print(path_folder)

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
            print("Export {}x = {}".format(len(all_data),path_full))
            platforms.platforms[target_platform].file_export(path_full)

            # Delete export_meshes
            bpy.ops.object.delete()
            export_meshes.clear()
            
            # Restore names
            restore_defaults(all_data)

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
        