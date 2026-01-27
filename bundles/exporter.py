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

# The exporter works by duplicating out a copy of the bundled objects into a 'shadow' copy.
# On this copy we can apply all of the destructive modifiers, changes, renames, etc. 
# We then export that copy.

# Notes:
# Due to Blender requiring a global unique name for every object, and the exported object needing to have
# the 'true' name for the object, we have to first rename the original objects before export. Later we reset 
# the names back to originals. 

class Exporter():
    def __init__(self, bundle, path, export_format, export_preset):
        self.bundle = bundle
        self.path = path
        self.export_format = export_format
        self.export_preset = export_preset

    # https://blenderartists.org/t/using-fbx-export-presets-when-exporting-from-a-script/1162914
    def get_export_arguments(self):
        filepath = settings.get_presets(self.export_format)[self.export_preset]

        class Container(object):
            __slots__ = ('__dict__',)

        op = Container()
        file = open(filepath, 'r')

        # storing the values from the preset on the class
        for line in file.readlines()[3::]:
            exec(line, globals(), locals())

        kwargs = op.__dict__
        operator = settings.export_operators[self.export_format]
        valid_props = operator.get_rna_type().properties.keys()
        kwargs = {k: v for k, v in kwargs.items() if k in valid_props}

        # Active collection filtering breaks bundle export since we select
        # specific objects to export, not whatever collection is active.
        if 'use_active_collection' in kwargs:
            kwargs['use_active_collection'] = False

        return kwargs

    def __enter__(self):
        objects = self.bundle.objects
        orig_obj_names = set([x.name for x in objects])
        print('Objects to export: {}'.format(objects))
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
            obj['__orig_hide_vl__'] = obj.hide_get()

            if obj.animation_data and obj.animation_data.action:
                obj['__orig_action__'] = obj.animation_data.action
                obj.animation_data.action = None

            obj.hide_viewport = False
            obj.hide_select = False
            obj.hide_set(False)

            if obj in objects:
                try:
                    obj.select_set(True)
                except RuntimeError:
                    pass
                obj.name = prefix_copy + obj.name
            else:
                try:
                    obj.select_set(False)
                except RuntimeError:
                    pass

        # 1. Duplicate objects (currently linked to the shared collection)
        bpy.ops.object.duplicate()
        
        # Capture the duplicates immediately (Blender selects duplicates automatically)
        copied_objects = [x for x in bpy.context.selected_objects]

        # 2. Create a temporary scene for isolation
        self.orig_scene = bpy.context.scene
        self.export_scene = bpy.data.scenes.new(name="BGE_Export_Staging")

        # 3. Move duplicates to the temporary scene
        # We explicitly link to the new scene and unlink from ALL old collections
        # to ensure they no longer exist in the shared 'Hub' collection.
        for obj in copied_objects:
            self.export_scene.collection.objects.link(obj)
            for coll in obj.users_collection:
                if coll != self.export_scene.collection:
                    coll.objects.unlink(obj)

        # 4. Switch context to the new scene
        # This ensures subsequent operations happen in the isolated environment
        bpy.context.window.scene = self.export_scene

        # 5. Re-establish selection in the new scene
        bpy.ops.object.select_all(action='DESELECT')
        for obj in copied_objects:
            obj.select_set(True)

        # 6. Make Single User
        # This makes sure that all of the data blocks used by the exported and 
        # soon-to-be-modified objects are not going to affect the original scene. 
        bpy.ops.object.make_local(type='SELECT_OBDATA') # Instantiate linked objects from other files into this scene. 
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)
        
        # Refresh list in case object references changed (unlikely here but safe practice)
        copied_objects = [x for x in bpy.context.selected_objects]

        # mark copied objects for later deletion
        for x in copied_objects:
            x['__IS_COPY__'] = True
            x.name = x['__orig_name__']

        bundle_info = self.bundle.create_bundle_info()
        bundle_info['meshes'] = [x for x in copied_objects if x.type in mesh_types]
        bundle_info['empties'] = [x for x in copied_objects if x.type in empty_types]
        bundle_info['armatures'] = [x for x in copied_objects if x.type in armature_types]
        bundle_info['path'] = self.path
        bundle_info['export_format'] = self.export_format
        bundle_info['export_preset'] = self.get_export_arguments()

        self.bundle_info = bundle_info
        return bundle_info

    def __exit__(self, type, value, traceback):
        if settings.debug:
            return

        # We must return to the original scene before deleting the export scene
        bpy.context.window.scene = self.orig_scene

        # Delete the duplicated 'export' objects.
        # We iterate bpy.data.objects because they might be in the other scene
        for obj in list(self.export_scene.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

        # Delete the temporary export scene. 
        bpy.data.scenes.remove(self.export_scene)

        # now restore original values
        objs = [x for x in bpy.data.objects]
        for obj in objs:
            if obj.name != obj['__orig_name__']:
                obj.name = obj['__orig_name__']
            obj.hide_viewport = obj['__orig_hide__']
            obj.hide_select = obj['__orig_hide_select__']
            obj.hide_set(bool(obj['__orig_hide_vl__']))

            if '__orig_action__' in obj:
                obj.animation_data.action = obj['__orig_action__']
                del obj['__orig_action__']

            del obj['__orig_name__']
            del obj['__orig_hide__']
            del obj['__orig_hide_select__']
            del obj['__orig_hide_vl__']
            del obj['__orig_collection__']

        for collection in bpy.data.collections:
            collection.hide_viewport = collection['__orig_hide__']
            collection.hide_select = collection['__orig_hide_select__']

            del collection['__orig_hide__']
            del collection['__orig_hide_select__']

        layers_in_hierarchy = reversed(list(traverse_tree(bpy.context.view_layer.layer_collection, exclude_parent=True)))
        for layer_collection in layers_in_hierarchy:
            if '__orig_exclude__' in bpy.data.collections[layer_collection.name]:
                layer_collection.exclude = bpy.data.collections[layer_collection.name]['__orig_exclude__']
                del bpy.data.collections[layer_collection.name]['__orig_exclude__']
            if '__orig_hide_lc__' in bpy.data.collections[layer_collection.name]:
                layer_collection.hide_viewport = bpy.data.collections[layer_collection.name]['__orig_hide_lc__']
                del bpy.data.collections[layer_collection.name]['__orig_hide_lc__']

        # remove unused meshes
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

        for modifier in self.bundle.modifiers:
            print('Clean up modifier "{}" ...'.format(modifier.id))
            modifier.post_export(self.bundle_info)


def _is_relative_path(path):
    """Check if a path is relative (not absolute and not empty)."""
    if not path:
        return False
    # Blender's '//' prefix denotes blend-file-relative paths
    if path.startswith('//'):
        return True
    # Standard relative paths like '../' or 'subdir/'
    if not os.path.isabs(path):
        return True
    return False


def export(bundles):
    start_time = time.time()

    # Validate that relative paths can be resolved.
    # Relative paths (like '../' or '//') need the blend file to be saved first,
    # because they are resolved relative to the blend file's location on disk.
    # Without a saved file, there's no directory to resolve from.
    export_path = bpy.context.scene.BGE_Settings.path
    if _is_relative_path(export_path) and not bpy.data.is_saved:
        def draw_error(self, context):
            self.layout.label(text=f"A relative export path ({export_path}) requires the blend file to be saved first.")
            self.layout.label(text="Save your file or use an absolute path.")
        bpy.context.window_manager.popup_menu(draw_error, title="Cannot Export", icon='ERROR')
        return

    previous_selection = bpy.context.selected_objects.copy()
    previous_active = bpy.context.view_layer.objects.active
    previous_unit_system = bpy.context.scene.unit_settings.system
    previous_pivot = bpy.context.scene.tool_settings.transform_pivot_point
    previous_cursor = bpy.context.scene.cursor.location

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    if bpy.context.view_layer.objects.active:
        bpy.context.view_layer.objects.active = None

    # bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

    processed_bundles = 0

    for bundle in bundles:
        processed_bundles += 1
        with Exporter(bundle, bpy.context.scene.BGE_Settings.path, bpy.context.scene.BGE_Settings.export_format, bpy.context.scene.BGE_Settings.export_preset) as bundle_info:
            all_objects = bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']
            print('Copied objects to export: {}'.format(all_objects))

            #assert False
            bpy.ops.object.select_all(action="DESELECT")
            for modifier in bundle.modifiers:
                print('Pre-processing modifier "{}" ...'.format(modifier.id))
                modifier.pre_process(bundle_info)

            for modifier in bundle.modifiers:
                print('Appliying modifier "{}" ...'.format(modifier.id))
                modifier.process(bundle_info)
            # apply the pivot
            all_objects = bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']

            print('objects after modifiers: {}'.format(all_objects))

            for x in all_objects:
                if x.parent and x.parent in all_objects:
                    continue
                x.location -= bundle_info['pivot']

            # Resolve the export path to an absolute path.
            #
            # Path resolution requires the blend file to be saved when using relative paths,
            # because we need a known location on disk to resolve paths like '../' from.
            # The validation at the start of export() ensures this precondition is met.
            #
            # bpy.path.abspath() handles Blender's '//' prefix (blend-file-relative notation),
            # but standard relative paths like '../' need additional handling - we resolve
            # them relative to the blend file's parent directory.
            export_path = bundle_info['path']
            blend_dir = os.path.dirname(bpy.data.filepath)
            # First expand '//' prefix if present
            export_path = bpy.path.abspath(export_path)
            # If still relative (e.g. '../subfolder'), resolve from the blend file's directory
            if not os.path.isabs(export_path):
                export_path = os.path.normpath(os.path.join(blend_dir, export_path))

            path_full = os.path.join(export_path, bundle_info['name']) + "." + settings.export_format_extensions[bundle_info['export_format']]
            directory = os.path.dirname(path_full)
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

            # Select all export objects
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action="DESELECT")
            for obj in bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']:
                obj.select_set(True)

            bundle_info['export_preset']['filepath'] = path_full
            operator = settings.export_operators[bundle_info['export_format']]
            valid_props = operator.get_rna_type().properties.keys()

            if 'use_selection' in valid_props:
                bundle_info['export_preset']['use_selection'] = True
            elif 'export_selected_objects' in valid_props:
                bundle_info['export_preset']['export_selected_objects'] = True

            settings.export_operators[bundle_info['export_format']](**bundle_info['export_preset'])

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

    bpy.context.window_manager.popup_menu(draw, title=f"Exported {processed_bundles}x bundles", icon='INFO')

    print("Exported in {} seconds".format(str(datetime.timedelta(seconds=(time.time() - start_time)))))
