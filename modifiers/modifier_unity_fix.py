import bpy
import imp

from . import modifier


class BGE_mod_unity_fix(modifier.BGE_mod_default):
    label = "Unity Fix"
    id = 'unity_fix'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'GENERAL'
    icon = 'NODE'
    tooltip = 'Fixes rotations of children when exporting to unity'
    priority = 9999999

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

    def process(self, bundle_info):
        meshes = bundle_info['meshes']

        bpy.context.view_layer.objects.active = None

        parents = [x for x in meshes if x.parent not in meshes]

        for x in parents:
            parent = x.parent
            matrixcopy = x.matrix_world.copy()
            x.parent = None
            x.matrix_world = matrixcopy

            children = [y for y in x.children]

            for y in children:
                matrixcopy = y.matrix_world.copy()
                y.parent = None
                y.matrix_world = matrixcopy

            bpy.ops.object.select_all(action='DESELECT')
            x.select_set(True)
            bpy.context.view_layer.objects.active = x

            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False, properties=False)
            bpy.ops.transform.rotate(value=-1.5708, orient_axis='X', constraint_axis=(True, False, False), orient_type='GLOBAL')

            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False, properties=False)
            bpy.ops.transform.rotate(value=1.5708, orient_axis='X', constraint_axis=(True, False, False), orient_type='GLOBAL')

            if parent:
                x.parent = parent
                x.matrix_parent_inverse = parent.matrix_world.inverted()

            for y in children:
                y.parent = x
                y.matrix_parent_inverse = x.matrix_world.inverted()
