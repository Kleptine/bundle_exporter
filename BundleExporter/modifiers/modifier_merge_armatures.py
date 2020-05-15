import bpy
import imp
import string
import random
import re
from mathutils import Vector

from . import modifier

from ..utilities import traverse_tree_from_iteration


class BGE_mod_merge_armatures(modifier.BGE_mod_default):
    label = "Merge Armatures"
    id = 'merge_armatures'
    url = "http://renderhjs.net/fbxbundle/#modifier_merge"
    type = 'ARMATURE'
    icon = 'CON_ARMATURE'
    priority = -1
    tooltip = 'Joins armatures and actions when exporting'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    create_root_bone: bpy.props.BoolProperty(
        name="Create Root Bone",
        default=True
    )

    root_bone_name: bpy.props.StringProperty(
        name='Root Name',
        default="root"
    )

    rename_bones: bpy.props.BoolProperty(
        name="Rename Bones",
        default=True
    )

    merge_actions: bpy.props.BoolProperty(
        name="Merge Actions",
        default=True
    )

    armature_name: bpy.props.StringProperty(
        name='Armature Name',
        default="MergedArmature"
    )

    new_name: bpy.props.StringProperty(
        name='Bone Name',
        default="{armature.name}_{name}"
    )

    def draw(self, layout):
        super().draw(layout)
        if(self.active):
            row = layout.row()
            row.separator()
            col = row.column(align=False)
            row = col.row(align=True)
            row.prop(self, 'create_root_bone')
            row.prop(self, 'root_bone_name', text='')
            col.prop(self, 'armature_name')
            row = col.row(align=True)
            row.prop(self, "rename_bones", text='')
            if self.rename_bones:
                row.prop(self, "new_name", text='Rename Data')
            col.prop(self, 'merge_actions')

    def process(self, bundle_info):
        armatures = bundle_info['armatures']
        objects = bundle_info['meshes']
        if not len(armatures) > 1:
            return False

        # gather merged actions data
        baked_merge_actions = {}
        if self.merge_actions:

            # for each armature search corresponding actions
            for armature in armatures:
                # loop though actions to search the ones to merge
                action_match_pattern = self.new_name.format(armature=armature, name='') # for example: 'myarmature@hand' will search for 'myarmature@' and therefore 'hand' is the name of the action
                for action in bpy.data.actions:
                    match = re.search(action_match_pattern, action.name)
                    if match:
                        match = action.name[match.start():match.end()]
                        new_action_name = action.name.replace(match, '')
                        if new_action_name not in baked_merge_actions:
                            baked_merge_actions[new_action_name] = {}
                        baked_merge_actions[new_action_name][action.name] = {}

                        actions_data = baked_merge_actions[new_action_name][action.name]

                        # assign the action to record
                        if armature.animation_data:
                            armature.animation_data.action = None
                            armature.animation_data_clear()
                        armature.animation_data_create()
                        armature.animation_data.action = action

                        for f in range(int(action.frame_range[0]), int(action.frame_range[1])):
                            if f not in actions_data:
                                actions_data[f] = {}
                            bpy.context.scene.frame_set(f)
                            # gets the transform of all the deform bones for each frame
                            for bone in armature.pose.bones:
                                if bone.bone.use_deform: # after disabling this check, the animation was correctly exported
                                    frame_data = {}
                                    matrix = armature.convert_space(pose_bone=bone, matrix=bone.matrix, from_space='POSE', to_space='LOCAL')

                                    frame_data['matrix'] = matrix
                                    frame_data['location'] = bone.location.copy()
                                    frame_data['scale'] = bone.scale.copy()
                                    frame_data['rotation'] = bone.rotation_quaternion.copy()
                                    actions_data[f][self.new_name.format(armature=armature, name=bone.name)] = frame_data

        bpy.ops.object.select_all(action='DESELECT')
        for x in armatures:
            x.select_set(True)
            if x.animation_data:
                x.animation_data_clear()

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
                    bone.name = self.new_name.format(armature=armature, name=bone.name)

        # join the armatures
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armatures[0]
        for x in armatures:
            print(x)
            x.select_set(True)
        bpy.ops.object.join()

        merged_armature = armatures[0]

        # make the old obj modifiers (like armatures) point to the new armature
        bpy.context.view_layer.objects.active = merged_armature
        for x in data_to_change:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            obj = bpy.data.objects[x]
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            for y in data_to_change[x]:
                mod = obj.modifiers[y]
                mod.object = merged_armature
                if 'subtarget' in data_to_change[x][y]:
                    mod.subtarget = data_to_change[x][y]['subtarget']

        # unhide all layers to select all bones and reset their transforms
        if merged_armature.animation_data:
            merged_armature.animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for x in range(0, 32):
            merged_armature.data.layers[x] = True

        for x in merged_armature.data.bones:
            x.driver_remove('hide_select')
            x.hide_select = False
            x.driver_remove('hide')
            x.hide = False
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()

        # create a new root bone for all the bones
        if self.create_root_bone:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            root_bone = merged_armature.data.edit_bones.new(self.root_bone_name)
            root_bone.head = Vector((0, 0, 0))
            root_bone.tail = Vector((0, 1, 0))
            for x in merged_armature.data.edit_bones:
                if not x.parent and x.name != root_bone:
                    x.parent = root_bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        merged_armature.name = self.armature_name
        merged_armature.data.name = self.armature_name + '.data'

        # merge actions now
        if self.merge_actions:
            options = {'INSERTKEY_NEEDED'}

            bpy.context.view_layer.objects.active = merged_armature
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            # delete all constraints
            for bone in merged_armature.pose.bones:
                for i in reversed(range(0, len(bone.constraints))):
                    bone.constraints.remove(bone.constraints[i])

            merged_armature.animation_data_create()
            for action_name, actions in baked_merge_actions.items():
                # if the merged action exists, delete it
                if action_name in bpy.data.actions:
                    bpy.data.actions.remove(bpy.data.actions[action_name])
                # create a new action with the merged name and assign it
                new_action = bpy.data.actions.new(action_name)
                merged_armature.animation_data.action = new_action

                # loop though all the actions to merge
                for action_info in actions.values():

                    for bone in traverse_tree_from_iteration(bone for bone in merged_armature.pose.bones if not bone.parent):
                        bone.rotation_mode = 'QUATERNION'
                        quat_prev = None

                        for frame, frame_data in action_info.items():
                            if bone.name in frame_data.keys():
                                matrix = frame_data[bone.name]['matrix']
                                bone.matrix_basis = matrix.copy()

                                bone.keyframe_insert("location", index=-1, frame=frame, group=bone.name, options=options)

                                if quat_prev is not None:
                                    quat = bone.rotation_quaternion.copy()
                                    quat.make_compatible(quat_prev)
                                    bone.rotation_quaternion = quat
                                    quat_prev = quat
                                    del quat
                                else:
                                    quat_prev = bone.rotation_quaternion.copy()

                                bone.keyframe_insert("rotation_quaternion", index=-1, frame=frame, group=bone.name, options=options)
                                bone.keyframe_insert("scale", index=-1, frame=frame, group=bone.name, options=options)
                            else:
                                pass

        # clear all transform data
        if merged_armature.animation_data:
            merged_armature.animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bundle_info['armatures'] = [merged_armature]
