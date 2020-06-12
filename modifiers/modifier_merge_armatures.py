import bpy
import imp
import string
import random
import re
from mathutils import Vector, Matrix

from . import modifier

from ..utilities import traverse_tree_from_iteration, isclose_matrix, matrix_to_list
from .. import settings


class BGE_mod_merge_armatures(modifier.BGE_mod_default):
    label = "Merge Armatures"
    id = 'merge_armatures'
    url = "http://renderhjs.net/fbxbundle/#modifier_merge"
    type = 'ARMATURE'
    icon = 'CON_ARMATURE'
    priority = -2
    tooltip = 'Joins armatures and actions when exporting'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
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

    def _draw_info(self, layout):
        col = layout.column(align=False)
        row = col.row(align=True)
        row.prop(self, 'create_root_bone')
        row.prop(self, 'root_bone_name', text='')
        col.prop(self, 'armature_name')
        row = col.row(align=True)
        row.prop(self, "rename_bones", text='Rename Data')
        if self.rename_bones:
            row.prop(self, "new_name", text='')
        col.prop(self, 'merge_actions')

    def process(self, bundle_info):
        created_actions = []
        armatures = bundle_info['armatures']
        objects = bundle_info['meshes']
        if not len(armatures) > 1:
            print('Not enoug armatures ')
            return False

        # gather merged actions data
        baked_merge_actions = {}
        if self.merge_actions:

            # for each armature search corresponding actions
            for armature in armatures:
                # loop though actions to search the ones to merge
                action_match_pattern = self.new_name.format(armature=armature, name='')  # for example: 'myarmature@hand' will search for 'myarmature@' and therefore 'hand' is the name of the action
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
                        if not armature.animation_data:
                            armature.animation_data_create()
                        armature.animation_data.action = action

                        for f in range(int(action.frame_range[0]), int(action.frame_range[1] + 1)):
                            if f not in actions_data:
                                actions_data[f] = []
                            bpy.context.scene.frame_set(f)
                            bpy.context.view_layer.update()
                            # gets the transform of all the deform bones for each frame
                            # order from root to children here, make array with tuple (bone.name, frame_data) instead of a dictionary for each frame values
                            for bone in traverse_tree_from_iteration(bone for bone in armature.pose.bones if not bone.parent):
                                if bone.bone.use_deform:  # only store information of deform bones
                                    frame_data = {}
                                    parent = bone.parent
                                    if parent and parent.bone.use_deform:
                                        # https://blender.stackexchange.com/questions/44637/how-can-i-manually-calculate-bpy-types-posebone-matrix-using-blenders-python-ap
                                        created_base_matrix = (parent.matrix.copy() @ (parent.bone.matrix_local.copy().inverted() @ bone.bone.matrix_local))  # this should be like rest pose

                                        rot_mat = created_base_matrix.to_quaternion().to_matrix().to_4x4()
                                        loc_mat = Matrix.Translation(created_base_matrix.to_translation()).to_4x4()

                                        # depending on the inherit scale / rotation/ scale we should create a new base matrrix below
                                        # in this case I chose every bone to inherit location and rotation but not scale (done below after the merge)
                                        created_base_matrix = loc_mat @ rot_mat  # and ignore scaling
                                        # all this should be equal to bone.matrix_basis
                                        frame_data['created_matrix_basis'] = created_base_matrix.inverted() @ bone.matrix
                                    else:
                                        frame_data['created_matrix_basis'] = bone.bone.matrix_local.copy().inverted() @ bone.matrix

                                    frame_data['matrix_world'] = armature.convert_space(pose_bone=bone, matrix=bone.matrix, from_space='POSE', to_space='WORLD')
                                    actions_data[f].append((self.new_name.format(armature=armature, name=bone.name), frame_data))

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

        # rename armature bones (vertex groups should update themselves with this)
        if self.rename_bones:
            for armature in armatures:
                for bone in armature.data.bones:
                    bone.name = self.new_name.format(armature=armature, name=bone.name)

        # join the armatures
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armatures[0]
        for x in armatures:
            x.select_set(True)
        bpy.ops.object.join()

        merged_armature = armatures[0]

        # make the old obj modifiers (like armatures) point to the new armature
        for x in data_to_change:
            obj = bpy.data.objects[x]
            for y in data_to_change[x]:
                mod = obj.modifiers[y]
                mod.object = merged_armature
                if 'subtarget' in data_to_change[x][y]:
                    mod.subtarget = data_to_change[x][y]['subtarget']

        # ---------------------------------------------------------------------------- #
        #                               ARMATURE CLEANUP                               #
        # ---------------------------------------------------------------------------- #

        # delete bones that dont deform
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        deleteBones = []
        for eb in merged_armature.data.edit_bones:
            if not eb.use_deform:
                deleteBones.append(eb)
        for db in deleteBones:
            merged_armature.data.edit_bones.remove(db)

        # unhide all layers to select all bones and reset their transforms
        if not merged_armature.animation_data:
            merged_armature.animation_data_create()
        merged_armature.animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for x in range(0, 32):
            merged_armature.data.layers[x] = True

        # make all bones visible
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for x in merged_armature.data.bones:
            x.driver_remove('hide_select')
            x.hide_select = False
            x.driver_remove('hide')
            x.hide = False

        # unlocking all transformations (probably not necessary)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for x in merged_armature.pose.bones:
            x.lock_location = [False, False, False]
            x.lock_rotation = [False, False, False]
            x.lock_rotation_w = False
            x.lock_rotations_4d = False
            x.lock_scale = [False, False, False]

        # set inheritance flags
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for x in merged_armature.data.edit_bones:
            # x.parent = None
            x.inherit_scale = 'NONE'
            x.use_inherit_rotation = True
            x.use_local_location = True  # this now should match the matrix we created before
            x.use_connect = False

        # reset transforms of all bones (probably not necessary either)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
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

        # rename armature
        merged_armature.name = self.armature_name
        merged_armature.data.name = self.armature_name + '.data'

        error_bones = set()
        # merge actions now
        if self.merge_actions:
            bpy.context.view_layer.objects.active = merged_armature
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            # delete all constraints
            for bone in merged_armature.pose.bones:
                for i in reversed(range(0, len(bone.constraints))):
                    bone.constraints.remove(bone.constraints[i])
            #  https://developer.blender.org/T70551
            for action_name, actions in baked_merge_actions.items():
                print(action_name)
                created_actions.append(action_name)
                # if the merged action exists, delete it
                if action_name in bpy.data.actions:
                    bpy.data.actions.remove(bpy.data.actions[action_name])
                # create a new action with the merged name and assign it
                new_action = bpy.data.actions.new(action_name)
                merged_armature.animation_data.action = new_action

                bpy.context.view_layer.update()

                # loop though all the actions to merge
                for action_name, action_info in actions.items():
                    for frame, frame_tuples in action_info.items():
                        for bone_name, frame_data in frame_tuples:
                            bone = merged_armature.pose.bones[bone_name]
                            bone.rotation_mode = 'QUATERNION'
                            bone.matrix_basis = frame_data['created_matrix_basis'].copy()

                            if action_name in bone.keys():
                                quat = bone.rotation_quaternion.copy()
                                quat.make_compatible(bone[action_name])
                                bone.rotation_quaternion = quat
                                bone[action_name] = quat
                                del quat
                            else:
                                bone[action_name] = bone.rotation_quaternion.copy()

                            bone.keyframe_insert("location", index=-1, frame=frame, group=bone.name, options={'INSERTKEY_NEEDED'})
                            bone.keyframe_insert("rotation_quaternion", index=-1, frame=frame, group=bone.name, options={'INSERTKEY_NEEDED'})
                            bone.keyframe_insert("scale", index=-1, frame=frame, group=bone.name, options={'INSERTKEY_NEEDED'})
                    if settings.debug:
                        # this checks that all transforms were applied correctly
                        bpy.context.view_layer.update()
                        for frame, frame_tuples in action_info.items():
                            bpy.context.scene.frame_set(frame)
                            for bone_name, frame_data in frame_tuples:
                                bone = merged_armature.pose.bones[bone_name]
                                matrix = merged_armature.convert_space(pose_bone=bone, matrix=frame_data['matrix_world'], from_space='WORLD', to_space='POSE')
                                if not isclose_matrix(bone.matrix, matrix, abs_tol=0.01):
                                    error_bones.add(bone.name)
                                    print('DOUBLE CHECK ### INCORRECT ### f{} - {}'.format(frame, bone.name))
                                    print('W-{}'.format(matrix))
                                    print('CW-{}'.format(bone.matrix))
                                if not isclose_matrix(bone.matrix_basis, frame_data['created_matrix_basis'], abs_tol=0.01):
                                    error_bones.add(bone.name)
                                    print('CB-{}'.format(bone.matrix_basis))
                                    print('B-{}'.format(frame_data['created_matrix_basis']))

        # clear all transform data (probably not necessary...)
        if merged_armature.animation_data:
            merged_armature.animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if settings.debug:
            if error_bones:
                print('ERROR BONES:')
                for x in error_bones:
                    print(x)
            else:
                print('NO ERROR BONES')

        # https://blenderartists.org/t/understanding-lists-in-blender/667968
        # for deleting merged actions after export
        self['created_actions'] = created_actions

        bundle_info['armatures'] = [merged_armature]

