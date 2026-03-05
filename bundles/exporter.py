import bpy
from .. import settings

from ..settings import prefix_copy, mesh_types, empty_types, armature_types
from ..utilities import traverse_tree

# https://preshing.com/20110920/the-python-with-statement-by-example/
# instead of try finally


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
        contaminated = [
            obj.name for obj in bpy.data.objects
            if any(key in obj for key in settings.contamination_props_object)
        ]
        if contaminated:
            names = ', '.join(contaminated)
            raise RuntimeError(
                f"Stale export properties found on: {names}. "
                f"Use the Cleanup button in the Bundle Exporter panel to fix this."
            )

        objects = self.bundle.objects
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

        # Duplicate objects (Blender selects duplicates automatically).
        bpy.ops.object.duplicate()
        copied_objects = [x for x in bpy.context.selected_objects]

        # Move duplicates out of their sub-collections into the scene's root collection.
        # This isolates them from the shared collections that contain the originals,
        # preventing make_single_user from creating orphan objects.
        scene_root = bpy.context.scene.collection
        for obj in copied_objects:
            scene_root.objects.link(obj)
            for coll in list(obj.users_collection):
                if coll is not scene_root:
                    coll.objects.unlink(obj)

        bpy.ops.object.make_local(type='SELECT_OBDATA')
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

        # Re-fetch after make_single_user which can create new object IDs.
        copied_objects = [x for x in bpy.context.selected_objects]

        # Track copies in a set for cleanup in __exit__. Modifiers that create
        # additional objects during processing add to this set via bundle_info['_copies'].
        self.copies = set(copied_objects)

        for x in copied_objects:
            x.name = x['__orig_name__']

        bundle_info = self.bundle.create_bundle_info()
        bundle_info['meshes'] = [x for x in copied_objects if x.type in mesh_types]
        bundle_info['empties'] = [x for x in copied_objects if x.type in empty_types]
        bundle_info['armatures'] = [x for x in copied_objects if x.type in armature_types]
        bundle_info['_copies'] = self.copies
        bundle_info['path'] = self.path
        bundle_info['export_format'] = self.export_format
        bundle_info['export_preset'] = self.get_export_arguments()

        self.bundle_info = bundle_info
        return bundle_info

    def __exit__(self, type, value, traceback):
        if settings.debug:
            return
        # first delete duplicated objects
        for obj in list(self.copies):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except ReferenceError:
                pass  # already freed by Blender
        self.copies.clear()

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
