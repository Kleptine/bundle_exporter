import os
import pathlib
import time
import datetime

import bpy
from .. import settings

from ..settings import prefix_copy, mesh_types, empty_types, armature_types
from ..utilities import traverse_tree, traverse_tree_from_iteration

# https://preshing.com/20110920/the-python-with-statement-by-example/
# instead of try finally


class Exporter():
    def __init__(self, bundle, path):
        self.bundle = bundle
        self.path = path

    def __enter__(self):
        objects = self.bundle.objects
        bpy.ops.object.select_all(action="DESELECT")
        # we need to traverse the tree from child to parent or else the exclude property can be missed
        layers_in_hierarchy = reversed(list(traverse_tree(bpy.context.view_layer.layer_collection, exclude_parent=True)))
        for layer_collection in layers_in_hierarchy:
            bpy.data.collections[layer_collection.name]['__orig_exclude__'] = layer_collection.exclude
            bpy.data.collections[layer_collection.name]['__orig_hide_lc__'] = layer_collection.hide_viewport
            layer_collection.exclude = False
            layer_collection.hide_viewport = False

        for collection in bpy.data.collections:
            collection['__orig_hide__'] = collection.hide_viewport
            collection['__orig_hide_select__'] = collection.hide_select

            collection.hide_select = False
            collection.hide_viewport = False

        # when renaming objects bpy.data.objects changes?
        objs = [x for x in bpy.data.objects]
        for obj in objs:
            obj['__orig_name__'] = obj.name
            obj['__orig_hide__'] = obj.hide_viewport
            obj['__orig_hide_select__'] = obj.hide_select
            obj['__orig_collection__'] = obj.users_collection[0].name if obj.users_collection else '__NONE__'

            if obj.animation_data and obj.animation_data.action:
                obj['__orig_action__'] = obj.animation_data.action
                obj.animation_data.action = None

            obj.hide_viewport = False
            obj.hide_select = False

            if obj in objects:
                obj.select_set(True)
                obj.name = prefix_copy + obj.name
            else:
                obj.select_set(False)

        # duplicate the objects
        bpy.ops.object.duplicate()
        copied_objects = [x for x in bpy.context.scene.objects if x.select_get()]
        bpy.ops.object.make_local(type='SELECT_OBDATA')
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

        # mark copied objects for later deletion
        for x in copied_objects:
            x['__IS_COPY__'] = True
            x.name = x['__orig_name__']

        bundle_info = self.bundle.create_bundle_info()
        bundle_info['meshes'] = [x for x in copied_objects if x.type in mesh_types]
        bundle_info['empties'] = [x for x in copied_objects if x.type in empty_types]
        bundle_info['armatures'] = [x for x in copied_objects if x.type in armature_types]
        bundle_info['path'] = self.path

        return bundle_info

    def __exit__(self, type, value, traceback):
        if settings.debug:
            return
        # first delete duplicated objects
        objs = [x for x in bpy.data.objects]
        for obj in objs:
            if '__IS_COPY__' in obj and obj['__IS_COPY__']:
                bpy.data.objects.remove(obj, do_unlink=True)

        # now restore original values
        objs = [x for x in bpy.data.objects]
        for obj in objs:
            if obj.name is not obj['__orig_name__']:
                obj.name = obj['__orig_name__']
            obj.hide_viewport = obj['__orig_hide__']
            obj.hide_select = obj['__orig_hide_select__']

            if '__orig_action__' in obj:
                obj.animation_data.action = obj['__orig_action__']
                del obj['__orig_action__']

            del obj['__orig_name__']
            del obj['__orig_hide__']
            del obj['__orig_hide_select__']
            del obj['__orig_collection__']

        for collection in bpy.data.collections:
            collection.hide_viewport = collection['__orig_hide__']
            collection.hide_select = collection['__orig_hide_select__']

            del collection['__orig_hide__']
            del collection['__orig_hide_select__']

        layers_in_hierarchy = reversed(list(traverse_tree(bpy.context.view_layer.layer_collection, exclude_parent=True)))
        for layer_collection in layers_in_hierarchy:
            layer_collection.exclude = bpy.data.collections[layer_collection.name]['__orig_exclude__']
            layer_collection.hide_viewport = bpy.data.collections[layer_collection.name]['__orig_hide_lc__']
            del bpy.data.collections[layer_collection.name]['__orig_exclude__']
            del bpy.data.collections[layer_collection.name]['__orig_hide_lc__']

        # remove unused meshes
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)


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
    start_time = time.time()

    export_format = bpy.context.scene.BGE_Settings.export_format
    export_preset = bpy.context.scene.BGE_Settings.export_preset

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

    for bundle in bundles:
        with Exporter(bundle, path) as bundle_info:
            bpy.ops.object.select_all(action="DESELECT")
            print('Start applying modifiers...')
            for modifier in bundle.modifiers:
                print('Appliying modifier "{}" ...'.format(modifier.id))
                modifier.process(bundle_info)

            # apply the pivot
            for x in bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']:
                x.location -= bundle_info['pivot']

            path_full = os.path.join(bpy.path.abspath(bundle_info['path']), bundle_info['name']) + "." + extension

            # Create path if not yet available
            directory = os.path.dirname(path_full)
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

            # Select all export objects
            bpy.ops.object.select_all(action="DESELECT")
            for obj in bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']:
                obj.select_set(True)

            export_preset_path = settings.get_presets(export_format)[export_preset]
            settings.export_operators[export_format](**get_export_arguments(export_preset_path, path_full))

            for modifier in bundle.modifiers:
                print('Clean up modifier "{}" ...'.format(modifier.id))
                modifier.post_export()

    # TODO: add this final part into a except/finally scope ?
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
        self.layout.operator("wm.path_open", text=bpy.context.scene.BGE_Settings.path, icon='FILE_FOLDER').filepath = bpy.context.scene.BGE_Settings.path

    bpy.context.window_manager.popup_menu(draw, title="Exported {}x files".format(len(list(bundles))), icon='INFO')

    print("Exported in {} seconds".format(str(datetime.timedelta(seconds=(time.time() - start_time)))))
