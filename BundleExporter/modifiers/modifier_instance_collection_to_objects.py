import bpy
import bmesh
import mathutils
import imp

from . import modifier
from .. import settings
from ..utilities import traverse_tree

class BGE_mod_instance_collection_to_objects(modifier.BGE_mod_default):
    label = "Group Intstances to Objects"
    id = 'instance_collection_to_objects'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'GENERAL'
    icon = 'OUTLINER_OB_GROUP_INSTANCE'
    priority = -999
    tooltip = 'Instance collections will be treated as objects when exporting'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )

    export_hidden: bpy.props.BoolProperty(
        name="Export Hidden",
        default=False
    )

    def _draw_info(self, layout):
        layout.prop(self, 'export_hidden')

    def process(self, bundle_info):
        helpers = bundle_info['empties']
        for i in reversed(range(0, len(helpers))):
            x = helpers[i]
            if x.instance_type == 'COLLECTION' and x.instance_collection:

                if not self.export_hidden:
                    for collection in traverse_tree(x.instance_collection):
                        for obj in collection.objects:
                            obj['__do_export__'] = not (collection['__orig_hide__'] or ('__orig_hide_lc__' in collection and collection['__orig_hide_lc__']) or ('__orig_hide__' in obj and obj['__orig_hide__']))

                bpy.ops.object.select_all(action='DESELECT')
                x.select_set(True)
                bpy.ops.object.duplicates_make_real(use_base_parent=False, use_hierarchy=True)
                new_nodes = [obj for obj in bpy.context.scene.objects if obj.select_get() and obj != x]
                bpy.ops.object.make_local(type='SELECT_OBDATA')
                bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

                for y in new_nodes:
                    y['__orig_collection__'] = x.name
                    y['__IS_COPY__'] = True  # to automatically delete them after export

                exportable_nodes = [x for x in new_nodes if '__do_export__' not in x or x['__do_export__'] == 1]

                # remove helper from export
                bundle_info['empties'].pop(i)

                bundle_info['meshes'].extend(x for x in exportable_nodes if x.type in settings.mesh_types)
                bundle_info['empties'].extend(x for x in exportable_nodes if x.type in settings.empty_types)
                bundle_info['armatures'].extend(x for x in exportable_nodes if x.type in settings.armature_types)
