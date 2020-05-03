import bpy, bmesh
import imp
import string
import random
from mathutils import Vector

from . import modifier

class BGE_mod_merge_armatures(modifier.BGE_mod_default):
    label = "Merge Armatures"
    id = 'merge_armatures'
    url = "http://renderhjs.net/fbxbundle/#modifier_merge"
    type = 'ARMATURE'
    icon = 'CON_ARMATURE'
    priority = -1

    active: bpy.props.BoolProperty (
        name="Active",
        default=False
    )
    # consistent_normals = bpy.props.BoolProperty (
    # 	name="Make consistent Normals",
    # 	default=True
    # )

    def draw(self, layout):
        super().draw(layout)
        if(self.active):
            pass

    def process_objects(self, name, objects, helpers, armatures):
        if not len(armatures) > 1:
            return objects, helpers, armatures

        bpy.ops.object.select_all(action='DESELECT')
        for x in armatures:
            x.select_set(True)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        export_collection = bpy.data.collections.new('armature_join_temp_collection')
        bpy.context.scene.collection.children.link(export_collection)

        current_action = bpy.context.active_object.animation_data.action

        dup_armatures = []

        for x in armatures:
            if x.proxy:
                bpy.ops.object.select_all(action='DESELECT')
                collection = x.proxy_collection
                proxy = x.proxy

                collection_dup = collection.copy()
                export_collection.objects.link(collection_dup)
                collection_dup.select_set(True)

                bpy.ops.object.duplicates_make_real()

                bpy.ops.object.select_all(action='DESELECT')
                dup_armatures.append(export_collection.objects[proxy.name])
                export_collection.objects[proxy.name].select_set(True)
                x.select_set(True)
                bpy.context.view_layer.objects.active = x
                bpy.ops.object.make_links_data(type='ANIMATION')


        for x in export_collection.objects:
            x.select_set(True)
        bpy.ops.object.make_local(type='SELECT_OBDATA')
        

        data_to_change = {}
        for x in export_collection.objects:
            for y in x.modifiers:
                for z in range(1,len(dup_armatures)):
                    o = dup_armatures[z]
                    if y.object == o:
                        if x.name not in data_to_change:
                            data_to_change[x.name] ={}
                        data_to_change[x.name][y.name] = {}
                        data_to_change[x.name][y.name]['object'] = y.object
                        data_to_change[x.name][y.name]['subtarget'] = y.subtarget
                    else:
                        print("NO")
        print('###################################')
        print(data_to_change)
        print('###################################')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = dup_armatures[0]
        for x in dup_armatures:
            x.select_set(True)
        bpy.ops.object.join()

        dup_armatures[0].animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for x in range(0,32):
            dup_armatures[0].data.layers[x] = True
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()

        bpy.context.view_layer.objects.active = dup_armatures[0]
        for x in data_to_change:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            obj = export_collection.objects[x]
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            for y in data_to_change[x]:
                mod = obj.modifiers[y]
                mod.object = export_collection.objects[dup_armatures[0].name]
                mod.subtarget = data_to_change[x][y]['subtarget']

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        root_bone = dup_armatures[0].data.edit_bones.new('ROOT')
        root_bone.head = Vector((0,0,0))
        root_bone.tail = Vector((0,1,0))
        for x in dup_armatures[0].data.edit_bones:
            if not x.parent and x.name != root_bone:
                x.parent = root_bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        #copy_action = current_action.copy()
        #copy_action.name = 'EX.'+current_action.name
        dup_armatures[0].animation_data.action = current_action

        dup_armatures[0].name = 'EXPORT.ARMATURE.OBJ'
        dup_armatures[0].data.name = 'EXPORT.ARMATURE'

        print('EXPORTING....')
        bpy.ops.export_scene.fbx(   use_selection = True,
                                    object_types = {'ARMATURE', 'MESH'}, 
                                    bake_anim = True, 
                                    bake_anim_use_all_bones = True, 
                                    bake_anim_use_all_actions = True, 
                                    bake_anim_step = 1, 
                                    embed_textures = False, 
                                    axis_forward = '-Z', 
                                    axis_up = 'Y',
                                    use_armature_deform_only = True,
                                    filepath = bpy.path.abspath("//"+ export_name +".fbx"))
        print('DONE')

        #!CLEAN UP
        bpy.context.scene.collection.children.unlink(export_collection)
        objs = list(export_collection.objects)
        for x in reversed(range(0, len(objs))):
            obj_data = objs[x].data
            bpy.data.objects.remove(objs[x], do_unlink=True)

            if type(obj_data) == bpy.types.Armature:
                bpy.data.armatures.remove(obj_data, do_unlink=True)
            elif type(obj_data) == bpy.types.Curve:
                bpy.data.curves.remove(obj_data, do_unlink=True)
            elif type(obj_data) == bpy.types.Mesh:
                bpy.data.meshes.remove(obj_data, do_unlink=True)
        
        bpy.data.collections.remove(export_collection)

        return objects, helpers, armatures


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
    
    