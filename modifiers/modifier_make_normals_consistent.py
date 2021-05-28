import bpy
import imp

from . import modifier

class BGE_mod_make_normals_consistent(modifier.BGE_mod_default):
    label = "Make Normals Consistent"
    id = 'consistent_normals'
    type = 'MESH'
    icon = 'NORMALS_FACE'
    tooltip = 'Make Normals Consistent'
    priority = 100

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

        if meshes:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = meshes[0]
            for mesh in meshes:
                mesh.select_set(True)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            bpy.ops.mesh.normals_make_consistent()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
