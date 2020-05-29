import os
import bpy

from . import modifier


class BGE_mod_export_textures(modifier.BGE_mod_default):
    label = "Export Textures"
    id = 'export_textures'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'GENERAL'
    icon = 'FILE_IMAGE'
    priority = 99999
    tooltip = 'Assign a custom pivot by choosing a source object'

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
        textures = set()
        for ob in meshes:
            for mat_slot in ob.material_slots:
                if mat_slot.material:
                    if mat_slot.material.node_tree:
                        for x in mat_slot.material.node_tree.nodes:
                            if x.type == 'TEX_IMAGE':
                                textures.add(x.image)

        # https://devtalk.blender.org/t/saving-an-image-makes-it-darker-in-2-80/8525
        orig_view_transform = bpy.context.scene.view_settings.view_transform
        orig_file_format = bpy.context.scene.render.image_settings.file_format

        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        for x in textures:
            path = os.path.join(bpy.path.abspath(bundle_info['path']), x.name) + '.png'
            x.save_render(path, scene=bpy.context.scene)

        bpy.context.scene.view_settings.view_transform = orig_view_transform
        bpy.context.scene.render.image_settings.file_format = orig_file_format
