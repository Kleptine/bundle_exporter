import os
import pathlib

import bpy
from .. import settings

from ..settings import prefix_copy, mesh_types, empty_types, armature_types
from ..utilities import traverse_tree, traverse_tree_from_iteration

export_collection = None
debug = False

# copy all objects toguether to keep relations and store in them their original values
def copy_objects(objects):
    global export_collection

    bpy.ops.object.select_all(action="DESELECT")

    #TODO: maybe store the values for all the objects in the scene, that way we dont need to check if they are in an imported library
    for obj in objects:
        obj['__orig_name__'] = obj.name
        obj['__orig_hide__'] = obj.hide_viewport
        obj['__orig_hide_select__'] = obj.hide_select
        obj['__orig_collection__'] = obj.users_collection[0].name
        obj['__do_export__'] = True

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj # ?????
        obj.hide_viewport = False
        obj.hide_select = False
        obj.name = prefix_copy + obj.name
    
    # store the objects' original values and then rename as temp
    for collection in bpy.data.collections:
        collection['__orig_hide__'] = collection.hide_viewport
        collection['__orig_hide_select__'] = collection.hide_select

        if not collection.library:
            collection.hide_select = False
        else:
            # only visible objects will be exported from instanced collections
            # but to avoid breaking connections we need to make them visible before making them local
            #collection.hide_select = collection.hide_viewport# or collection.hide_select
            for obj in traverse_tree_from_iteration((x for x in collection.objects)):
                obj['__do_export__'] = not collection.hide_viewport
                # we need to also unhide these objects
                obj['__orig_hide__'] = obj.hide_viewport
                obj['__orig_hide_select__'] = obj.hide_select

                obj.hide_viewport = False
                obj.hide_select = False
                
        # for the instancing to work correctly all collections need to be visible, if not, make local can break connections and break rigs
        collection.hide_viewport = False

    for layer_collection in traverse_tree(bpy.context.view_layer.layer_collection, exclude_parent=True):
        bpy.data.collections[layer_collection.name]['__orig_exclude__'] = layer_collection.exclude
        layer_collection.exclude = False



    # duplicate the objects
    bpy.ops.object.duplicate()
    copied_objects = [x for x in bpy.context.scene.objects if x.select_get()]
    #bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=True, animation=False)

    #rename the duplicated objects to their real names
    for obj in copied_objects:
        obj.name = obj['__orig_name__']

    export_meshes = [x for x in copied_objects if x.type in mesh_types]
    export_helpers = [x for x in copied_objects if x.type in empty_types]
    export_armatures = [x for x in copied_objects if x.type in armature_types]

    return export_meshes, export_helpers, export_armatures


def restore_defaults(objects):
    for obj in objects:
        obj.name = obj['__orig_name__']
        obj.hide_viewport = obj['__orig_hide__']
        obj.hide_select = obj['__orig_hide_select__']

        del obj['__orig_name__']
        del obj['__orig_hide__']
        del obj['__orig_hide_select__']
        del obj['__orig_collection__']
        del obj['__do_export__']

    #make layers visible and selectable
    for collection in bpy.data.collections:
        collection.hide_viewport = collection['__orig_hide__']
        collection.hide_select = collection['__orig_hide_select__']

        del collection['__orig_hide__']
        del collection['__orig_hide_select__']

        if collection.library:
            for obj in traverse_tree_from_iteration((x for x in collection.objects)):
                obj.hide_viewport = obj['__orig_hide__']
                obj.hide_select = obj>['__orig_hide_select__']

                del obj['__do_export__']
                del obj['__orig_hide__']
                del obj['__orig_hide_select__']

    # to "unexclude" layers
    for layer_collection in traverse_tree(bpy.context.view_layer.layer_collection, exclude_parent=True):
        layer_collection.exclude = bpy.data.collections[layer_collection.name]['__orig_exclude__']
        del bpy.data.collections[layer_collection.name]['__orig_exclude__']


# https://blenderartists.org/t/using-fbx-export-presets-when-exporting-from-a-script/1162914
def get_export_arguments(filepath, export_path):
    class Container(object):
        __slots__ = ('__dict__',)

    op = Container()
    file = open(filepath, 'r')

    # storing the values from the preset on the class
    for line in file.readlines()[3::]:
        exec(line, globals(), locals())

    op.filepath = export_path
    kwargs = op.__dict__

    return kwargs


def export(bundles, path, export_format, export_preset):
    previous_selection = bpy.context.selected_objects.copy()
    previous_active = bpy.context.view_layer.objects.active
    previous_unit_system = bpy.context.scene.unit_settings.system
    previous_pivot = bpy.context.scene.tool_settings.transform_pivot_point
    previous_cursor = bpy.context.scene.cursor.location

    extension = settings.export_format_extensions[export_format]

    if bpy.context.view_layer.objects.active:
        bpy.context.view_layer.objects.active = None

    # bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

    exported = 0

    for bundle in bundles:
        exported += 1

        modifiers = bundle.modifiers
        name = bundle.key
        orig_objects = bundle.objects
        pivot = bundle.pivot

        export_meshes, export_helpers, export_armatures = copy_objects(orig_objects)

        bpy.ops.object.select_all(action="DESELECT")

        objects_to_delete = []

        try:
            # Apply modifiers
            path_folder = path
            path_name = name
            for modifier in bundle.modifiers:
                print(modifier.id)
                export_meshes, export_helpers, export_armatures, del_objs = modifier.process_objects(name, export_meshes, export_helpers, export_armatures)
                objects_to_delete.extend(del_objs)
                print(objects_to_delete)
                pivot = modifier.process_pivot(pivot, export_meshes, export_helpers, export_armatures)
                path_folder = modifier.process_path(path_name, path_folder)
                path_name = modifier.process_name(path_name)

            path_folder = bpy.path.abspath(path_folder)
            print(path_folder)

            for x in export_meshes + export_helpers + export_armatures:
                x.location -= pivot

            print(export_meshes)
            print(export_helpers)
            print(export_armatures)

            path_full = os.path.join(path_folder, path_name) + "." + extension

            # Create path if not yet available
            directory = os.path.dirname(path_full)
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

            # Select all export objects
            bpy.ops.object.select_all(action="DESELECT")
            for obj in export_meshes + export_helpers + export_armatures:
                obj.select_set(True)

            # Export per platform (Unreal, Unity, ...)
            print("Export {}x = {}".format(len(orig_objects),path_full))
            export_preset_path = settings.get_presets(export_format)[export_preset]
            settings.export_operators[export_format](**get_export_arguments(export_preset_path, path_full))
        finally:
            if not debug:
                all_meshes = export_meshes + export_helpers + export_armatures + objects_to_delete
                scene_objs = [x for x in bpy.data.objects]
                # sometimes objects have already been deleted and it can produce more error to just delete from the export obj arrays
                # so I loop through all the objects to see if they are the ones duplicated
                for obj in scene_objs:
                    if obj in all_meshes:
                        bpy.data.objects.remove(obj, do_unlink=True)

                # Restore names
                restore_defaults(orig_objects)

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
            filenames.append(name + "." + extension)

        self.layout.label(text="Exported:")
        for x in filenames:
            self.layout.label(text=x)

        self.layout.operator("wm.path_open", text=path, icon='FILE_FOLDER').filepath = path

    bpy.context.window_manager.popup_menu(draw, title="Exported {}x files".format(exported), icon='INFO')
