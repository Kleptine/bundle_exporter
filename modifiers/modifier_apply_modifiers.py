import bpy
import imp

from . import modifier

class BGE_mod_Apply_modifiers(modifier.BGE_mod_default):
    label = "Apply Modifiers"
    id = 'apply_modifiers'
    type = 'MESH'
    icon = 'CHECKMARK'
    tooltip = 'Apply Modifiers'
    priority = -9999

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
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
