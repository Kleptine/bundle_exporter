import bpy, bmesh, mathutils
import imp

from . import modifier
from .. import settings

class BGE_mod_instance_collection_to_objects(modifier.BGE_mod_default):
    label = "Group Intstances to Objects"
    id = 'instance_collection_to_objects'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'HELPER'
    icon = 'OUTLINER_OB_GROUP_INSTANCE'
    priority = -999

    active: bpy.props.BoolProperty (
        name="Active",
        default=False
    )

    def draw(self, layout):
        super().draw(layout)

    def process_objects(self, name, objects, helpers, armatures):
        for i in reversed(range(0, len(helpers))):
            x = helpers[i]
            if x.instance_type == 'COLLECTION' and x.instance_collection:
                bpy.ops.object.select_all(action='DESELECT')
                x.select_set(True)
                bpy.ops.object.duplicates_make_real()
                new_nodes = [obj for obj in bpy.context.scene.objects if obj.select_get() and obj != x]

                #remove helper from export
                helpers.pop(i)
                #delete helper
                bpy.ops.object.select_all(action='DESELECT')
                x.select_set(True)
                bpy.ops.object.delete()

                objects.extend(x for x in new_nodes if x.type in settings.mesh_types)
                helpers.extend(x for x in new_nodes if x.type in settings.empty_types)
                armatures.extend(x for x in new_nodes if x.type in settings.armature_types)

                others = (x for x in new_nodes if x not in objects and x not in helpers and x not in armatures)

                #delete the rest of the nodes
                bpy.ops.object.select_all(action='DESELECT')
                for y in others:
                    y.select_set(True)
                bpy.ops.object.delete()

        return objects, helpers, armatures