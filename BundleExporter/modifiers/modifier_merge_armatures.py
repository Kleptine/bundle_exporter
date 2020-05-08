import bpy
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

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    create_root_bone: bpy.props.BoolProperty(
        name="Create Root Bone",
        default=True
    )

    rename_bones: bpy.props.BoolProperty(
        name="Rename Bones",
        default=True
    )

    armature_name: bpy.props.StringProperty(
        name='Armature Name',
        default="MergedArmature"
    )

    new_name: bpy.props.StringProperty(
        name='Bone Name',
        default="{armature.name}_{bone.name}"
    )

    def draw(self, layout):
        super().draw(layout)
        if(self.active):
            row = layout.row()
            row.separator()
            col = row.column()
            col.prop(self, 'create_root_bone')
            col.prop(self, 'armature_name')
            col.prop(self, "rename_bones")
            if self.rename_bones:
                col.prop(self, "new_name")

    def process_objects(self, name, objects, helpers, armatures):
        if not len(armatures) > 1:
            return objects, helpers, armatures

        bpy.ops.object.select_all(action='DESELECT')
        for x in armatures:
            x.select_set(True)

        # search for objects that have modifiers pointing to the armatures
        data_to_change = {}
        for x in objects:
            for y in x.modifiers:
                for z in range(1, len(armatures)):
                    o = armatures[z]
                    if hasattr(y, 'object') and y.object == o:
                        if x.name not in data_to_change:
                            data_to_change[x.name] = {}
                        data_to_change[x.name][y.name] = {}
                        data_to_change[x.name][y.name]['object'] = y.object
                        if hasattr(y, 'subtarget'):
                            data_to_change[x.name][y.name]['subtarget'] = y.subtarget

        print('###################################\n{}\n###################################'.format(data_to_change))

        # rename armature bones
        if self.rename_bones:
            for armature in armatures:
                for bone in armature.data.bones:
                    bone.name = self.new_name.format(armature=armature, bone=bone)

        # join the armatures
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armatures[0]
        for x in armatures:
            print(x)
            x.select_set(True)
        bpy.ops.object.join()

        # make the old modifiers point to the new armature
        bpy.context.view_layer.objects.active = armatures[0]
        for x in data_to_change:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            obj = bpy.data.objects[x]
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            for y in data_to_change[x]:
                mod = obj.modifiers[y]
                mod.object = armatures[0]
                if 'subtarget' in data_to_change[x][y]:
                    mod.subtarget = data_to_change[x][y]['subtarget']

        # unhide all layers to select all bones and reset their transforms
        if armatures[0].animation_data:
            armatures[0].animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for x in range(0, 32):
            armatures[0].data.layers[x] = True
        # TODO: do the same for the bone.hide property and unlink any driver assigned to it
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()

        # create a new root bone for all the bones
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        root_bone = armatures[0].data.edit_bones.new('ROOT')
        root_bone.head = Vector((0, 0, 0))
        root_bone.tail = Vector((0, 1, 0))
        for x in armatures[0].data.edit_bones:
            if not x.parent and x.name != root_bone:
                x.parent = root_bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        armatures[0].name = self.armature_name
        armatures[0].data.name = self.armature_name
        armatures = [armatures[0]]

        return objects, helpers, armatures


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
