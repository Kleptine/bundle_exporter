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
    type = 'HELPER'
    icon = 'OUTLINER_OB_GROUP_INSTANCE'
    priority = -999
    tooltip = 'Instance collections will be treated as objects when exporting'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    export_hidden: bpy.props.BoolProperty(
        name="Export Hidden",
        default=False
    )

    def draw(self, layout):
        super().draw(layout)
        if(self.active):
            row = layout.row()
            row.separator()
            row.prop(self, 'export_hidden')

    def process_objects(self, name, objects, helpers, armatures):
        objects_to_delete = []
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
                    y['__IS_COPY__'] = True

                exportable_nodes = [x for x in new_nodes if not '__do_export__' in x or x['__do_export__'] == 1]
                
                # remove helper from export
                helpers.pop(i)
                objects_to_delete.append(x)

                objects.extend(x for x in exportable_nodes if x.type in settings.mesh_types)
                helpers.extend(x for x in exportable_nodes if x.type in settings.empty_types)
                armatures.extend(x for x in exportable_nodes if x.type in settings.armature_types)

                others = (x for x in new_nodes if x not in objects and x not in helpers and x not in armatures)
                objects_to_delete.extend(others)

        return objects, helpers, armatures, objects_to_delete
