import bpy
import imp
import string
import random
import re
from mathutils import Vector, Matrix

from . import modifier

from ..utilities import traverse_tree_from_iteration, isclose_matrix, matrix_to_list
from .. import settings


class BGE_mod_bake_actions(modifier.BGE_mod_default):
    label = "Bake Actions"
    id = 'bake_actions'
    url = "http://renderhjs.net/fbxbundle/#modifier_merge"
    type = 'ARMATURE'
    icon = 'ACTION'
    priority = -3
    tooltip = 'Joins armatures and actions when exporting'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )

    def _draw_info(self, layout):
        pass

    def pre_process(self, bundle_info):
        def validate_actions(act, path_resolve):
            for fc in act.fcurves:
                data_path = fc.data_path
                if fc.array_index:
                    data_path = data_path + "[%d]" % fc.array_index
                try:
                    path_resolve(data_path)
                except ValueError:
                    return False
            return True

        baked_actions = {}

        for armature in bundle_info['armatures']:
            for action in bpy.data.actions:
                if validate_actions(action, armature.path_resolve):
                    if not armature.animation_data:
                        armature.animation_data_create()
                    armature.animation_data.action = action

                    baked_actions[action.name] = {}
                    actions_data = baked_actions[action.name]

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
                                actions_data[f].append(bone.name, frame_data)

            armature['__baked_action_data__'] = actions_data
