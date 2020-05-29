import os
import bpy

from . import modifier

file_formats_enum = {
    'BMP': '.bmp',
    'IRIS': '.sgi',
    'PNG': '.png',
    'JPEG': '.jpg',
    'JPEG2000': '.jp2',
    'TARGA': '.tga',
    'TARGA_RAW': '.tga',
    'CINEON': '.cin',
    'DPX': '.dpx',
    'OPEN_EXR_MULTILAYER': '.exr',
    'OPEN_EXR': '.exr',
    'HDR': '.hdr',
    'TIFF': '.tiff',
    'AVI_JPEG': '.avi',  # why not
    'AVI_RAW': '.avi',
    'FFMPEG': '.mkv'
}


class BGE_mod_export_textures(modifier.BGE_mod_default):
    label = "Export Textures"
    id = 'export_textures'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'GENERAL'
    icon = 'FILE_IMAGE'
    priority = 99999
    tooltip = 'Exports all textures being used by the exported objects to the same folder'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )

    path: bpy.props.StringProperty(default="{bundle_path}")
    file: bpy.props.StringProperty(default="{texture_name}")

    def _draw_info(self, layout):
        col = layout.column(align=True)
        col.prop(self, "path", text="Path")
        col.prop(self, "file", text="File")

        layout.template_image_settings(bpy.context.scene.render.image_settings, color_management=False)

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

        for x in textures:
            bundle_path = bpy.path.abspath(bundle_info['path'])
            folderpath = self.path.format(bundle_path=bundle_path)
            filename = self.file.format(texture_name=x.name) + file_formats_enum[orig_file_format]
            path = os.path.join(folderpath, filename)
            x.save_render(path, scene=bpy.context.scene)

        bpy.context.scene.view_settings.view_transform = orig_view_transform
        bpy.context.scene.render.image_settings.file_format = orig_file_format
