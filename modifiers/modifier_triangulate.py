import bpy
import imp

from . import modifier


class BGE_mod_triangulate(modifier.BGE_mod_default):
    label = "Triangulate"
    id = 'triangulate'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'MESH'
    icon = 'MOD_TRIANGULATE'
    tooltip = 'Applies the triangulate modifier (keeping normals)'
    priority = -1  # before the merge modifier

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

        for mesh in meshes:
            mod = mesh.modifiers.new('export_triangulate', type='TRIANGULATE')
            mod.keep_custom_normals = True
