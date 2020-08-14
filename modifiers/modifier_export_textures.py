import os
import bpy
import math
from . import modifier
import mathutils

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

# [(x.name, x.type)for x in C.object.material_slots[0].material.node_tree.nodes[1].inputs]
bsdf_inputs = {
    'Base Color': 'RGBA', 
    'Subsurface': 'VALUE', 
    'Subsurface Radius': 'VECTOR', 
    'Subsurface Color': 'RGBA', 
    'Metallic': 'VALUE', 
    'Specular': 'VALUE', 
    'Specular Tint': 'VALUE', 
    'Roughness': 'VALUE', 
    'Anisotropic': 'VALUE', 
    'Anisotropic Rotation': 'VALUE', 
    'Sheen': 'VALUE', 
    'Sheen Tint': 'VALUE', 
    'Clearcoat': 'VALUE', 
    'Clearcoat Roughness': 'VALUE', 
    'IOR': 'VALUE', 
    'Transmission': 'VALUE', 
    'Transmission Roughness': 'VALUE', 
    'Emission': 'RGBA', 
    'Alpha': 'VALUE', 
    'Normal': 'VECTOR', 
    'Clearcoat Normal': 'VECTOR', 
    'Tangent': 'VECTOR'
}

class BGE_OT_new_texture_packer(bpy.types.Operator):
    bl_idname = "ezb.new_texture_packer"
    bl_label = "New Texture Packer"

    def execute(self, context):
        mod = bpy.context.scene.BGE_Settings.scene_modifiers.BGE_modifier_export_textures
        mod.texture_packs.add()
        index=len(mod.texture_packs) - 1
        mod.texture_packs_index = index
        return {'FINISHED'}

class BGE_OT_remove_texture_packer(bpy.types.Operator):
    bl_idname = "ezb.remove_texture_packer"
    bl_label = "Remove Texture Packer"

    @classmethod
    def poll(cls, context):
        mod = bpy.context.scene.BGE_Settings.scene_modifiers.BGE_modifier_export_textures
        return len(mod.texture_packs) > mod.texture_packs_index

    def execute(self, context):
        mod = bpy.context.scene.BGE_Settings.scene_modifiers.BGE_modifier_export_textures
        mod.texture_packs.remove(mod.texture_packs_index)

        if mod.texture_packs_index >= len(mod.texture_packs):
            mod.texture_packs_index = len(mod.texture_packs)-1
        return {'FINISHED'}


class BGE_Texture_Packer(bpy.types.PropertyGroup):

    def get_bsdf_enum(self, context):
        return [(x, x, x, '', i) for i,x in enumerate(list(bsdf_inputs.keys()))]

    suffix: bpy.props.StringProperty(default='_MASK', name='Suffix')

    BW: bpy.props.EnumProperty(items=get_bsdf_enum)
    RGB: bpy.props.EnumProperty(items=get_bsdf_enum)
    RGBA: bpy.props.EnumProperty(items=get_bsdf_enum)
    R: bpy.props.EnumProperty(items=get_bsdf_enum)
    G: bpy.props.EnumProperty(items=get_bsdf_enum)
    B: bpy.props.EnumProperty(items=get_bsdf_enum)
    A: bpy.props.EnumProperty(items=get_bsdf_enum)

    BW_channel: bpy.props.EnumProperty(items=[('R', 'R', 'R'), ('G', 'G', 'G'), ('B', 'B', 'B'), ('A', 'A', 'A')], default = 'R')
    R_channel: bpy.props.EnumProperty(items=[('R', 'R', 'R'), ('G', 'G', 'G'), ('B', 'B', 'B'), ('A', 'A', 'A')], default = 'R')
    G_channel: bpy.props.EnumProperty(items=[('R', 'R', 'R'), ('G', 'G', 'G'), ('B', 'B', 'B'), ('A', 'A', 'A')], default = 'G')
    B_channel: bpy.props.EnumProperty(items=[('R', 'R', 'R'), ('G', 'G', 'G'), ('B', 'B', 'B'), ('A', 'A', 'A')], default = 'B')
    A_channel: bpy.props.EnumProperty(items=[('R', 'R', 'R'), ('G', 'G', 'G'), ('B', 'B', 'B'), ('A', 'A', 'A')], default = 'A')

    color_mode: bpy.props.EnumProperty(
       items=[
           ('BW', 'BW', 'Black and white'),

           ('RGB', 'RGB', 'Red, green, blue'),
           ('RGBA', 'RGBA', 'Red, green, blue, alpha'),

           ('R+G+B', 'R+G+B', 'Red, green, blue'),
           ('R+G+B+A', 'R+G+B+A', 'Red, green, blue, alpha'),

           ('RGB+A', 'RGB+A', 'Red, green, blue, alpha'),
       ],
       default='R+G+B',
       name='Mode'
    )
    color_depth: bpy.props.EnumProperty(
       items=[
           ('8', '8', '8'),
           ('16', '16', '16'),
       ],
       default='8',
       name='Depth'
    )

    def draw(self, layout):
        layout.prop(self, 'suffix')
        channels = self.color_mode.split('+')
        for channel in channels:
            show_channel = bsdf_inputs[getattr(self, channel)] in ['VECTOR', 'RGBA'] and channel not in ['RGB', 'RGBA']
            row = layout.split(factor=0.15, align=True)
            row.label(text=channel)
            if show_channel:
                row = row.split(factor=0.8, align=True)
            row.prop(self, channel, text='')
            if show_channel:
                row.prop(self, channel+'_channel', text='')



class BGE_UL_texture_packs(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, 'suffix', emboss=False, text='')
        layout.prop(item, 'color_mode', text='')
        layout.prop(item, 'color_depth', text='')


class BGE_mod_export_textures(modifier.BGE_mod_default):
    label = "Export Textures"
    id = 'export_textures'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'GENERAL'
    icon = 'FILE_IMAGE'
    priority = 99999
    tooltip = 'Exports all textures being used by the exported objects to the same folder'
    dependants = [BGE_Texture_Packer, BGE_UL_texture_packs, BGE_OT_new_texture_packer, BGE_OT_remove_texture_packer]

    export_method: bpy.props.EnumProperty(
        items=[
            ('EXPORT_ALL', 'Export All', 'Export all images found inside the exported materials'),
            ('PACK', 'Pack and Export', 'Combines textures into different channels before exporting')
        ]
    )

    texture_packs: bpy.props.CollectionProperty(type=BGE_Texture_Packer)
    texture_packs_index: bpy.props.IntProperty()

    image_format: bpy.props.EnumProperty(
       items=[
           ('TGA', 'TGA', 'Export images as .tga'),
           ('PNG', 'PNG', 'Export images as .png'),
           ('TIF', 'TIF', 'Export images as .tif'),
       ],
       default='PNG',
       name='Format'
    )

    color_mode: bpy.props.EnumProperty(
       items=[
           ('BW', 'BW', 'Black and white'),
           ('RGB', 'RGB', 'Red, green, blue'),
           ('RGBA', 'RGBA', 'Red, green, blue, alpha'),
       ],
       default='RGB',
       name='Mode'
    )
    color_depth: bpy.props.EnumProperty(
       items=[
           ('8', '8', '8'),
           ('16', '16', '16'),
       ],
       default='8',
       name='Depth'
    )


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

        col = layout.column(align=True)
        row = col.row()
        row.prop(self, "export_method", expand=True)

        layout.prop(self, 'image_format', text='Format', icon='IMAGE_DATA')

        if self.export_method == 'EXPORT_ALL':
            col2 = layout.column(align=True)
            col2.use_property_split = True
            col2.use_property_decorate = False
            row=col2.row(align=True)
            row.prop(self, 'color_mode', expand=True,)
            if not self.image_format == 'TARGA':
                row=col2.row(align=True)
                row.prop(self, 'color_depth', expand=True)
        elif self.export_method == 'PACK':
            row = layout.row(align=True)
            row.template_list("BGE_UL_texture_packs", "", self, "texture_packs", self, "texture_packs_index", rows=2)
            col = row.column(align=True)
            col.operator('ezb.new_texture_packer', text='', icon = 'ADD')
            col.operator('ezb.remove_texture_packer', text='', icon = 'REMOVE')

            if self.texture_packs_index >= 0 and self.texture_packs_index < len(self.texture_packs):
                texture_pack = self.texture_packs[self.texture_packs_index]
                texture_pack.draw(layout)

    def process(self, bundle_info):
        meshes = bundle_info['meshes']
        if not meshes:
            return
        
        folderpath = self.path.format(bundle_path=bundle_info['path'])

        view_transform = bpy.context.scene.view_settings.view_transform
        file_format = bpy.context.scene.render.image_settings.file_format
        color_mode = bpy.context.scene.render.image_settings.color_mode
        color_depth = bpy.context.scene.render.image_settings.color_depth
        compression = bpy.context.scene.render.image_settings.compression
        tiff_codec = bpy.context.scene.render.image_settings.tiff_codec

        bpy.context.scene.render.image_settings.file_format = self.image_format
        bpy.context.scene.render.image_settings.color_mode = self.color_mode
        bpy.context.scene.render.image_settings.color_depth = self.color_depth
        bpy.context.scene.render.image_settings.compression = 0
        bpy.context.scene.render.image_settings.tiff_codec = 'DEFLATE'
        bpy.context.scene.view_settings.view_transform = 'Standard'

        if self.export_method == 'EXPORT_ALL':
            textures = set()
            for ob in meshes:
                for mat_slot in ob.material_slots:
                    if mat_slot.material:
                        if mat_slot.material.node_tree:
                            for x in mat_slot.material.node_tree.nodes:
                                if x.type == 'TEX_IMAGE' and x.image:
                                    textures.add(x.image)
            for x in textures:
                filename = self.file.format(texture_name=x.name) + file_formats_enum[self.image_format]
                path = os.path.join(folderpath, filename)
                x.save_render(path, scene=bpy.context.scene)

        elif self.export_method == 'PACK':
            for ob in meshes:
                for mat_slot in ob.material_slots:
                    if mat_slot.material:
                        if mat_slot.material.node_tree:
                            try:
                                bsdf = next(x for x in mat_slot.material.node_tree.nodes if x.bl_rna.identifier == 'ShaderNodeBsdfPrincipled')
                            except StopIteration:
                                print(f'{mat_slot.material.name} has not principled bsdf material')

                            for texture_packer in self.texture_packs:
                                channels = texture_packer.color_mode.split('+')
                                

                                # get output image size
                                min_width = math.inf
                                min_height = math.inf
                                for channel in channels:
                                    input_name = getattr(texture_packer, channel)

                                    multi_channel = bsdf_inputs[input_name] in ['VECTOR', 'RGBA']
                                    
                                    if bsdf.inputs[input_name].is_linked:
                                        link = bsdf.inputs[input_name].links[0]
                                        if link.from_node.bl_rna.identifier == 'ShaderNodeTexImage':
                                            img = link.from_node.image
                                            if img:
                                                if img.size[0] < min_width:
                                                    min_width = img.size[0]
                                                if img.size[1] < min_height:
                                                    min_height = img.size[1]

                                if min_width == math.inf:
                                    min_width = 8
                                if min_height == math.inf:
                                    min_height = 8

                                #output image size is set

                                total_pixels = min_width*min_height

                                channel_data = {}
                                for channel in channels:
                                    input_name = getattr(texture_packer, channel)
                                    multi_channel = bsdf_inputs[input_name] in ['VECTOR', 'RGBA']
                                    current_data = None
                                    if bsdf.inputs[input_name].is_linked:
                                        link = bsdf.inputs[input_name].links[0]
                                        if link.from_node.bl_rna.identifier == 'ShaderNodeTexImage':
                                            img = link.from_node.image
                                            if img:
                                                copy_img = img.copy()

                                                copy_img.pack()
                                                copy_img.source = 'GENERATED'
                                                copy_img.scale(min_width, min_height)
                                                copy_img.pack()
                                                
                                                pixels = copy_img.pixels[:]

                                                if link.from_socket.name == 'Color':
                                                    current_data = [(pixels[i+0], pixels[i+1], pixels[i+2], pixels[i+3]) for i in range(0, int(len(pixels)), 4)]
                                                elif link.from_socket.name == 'Alpha':
                                                    current_data = [(pixels[i+3], pixels[i+3], pixels[i+3], pixels[i+3]) for i in range(0, int(len(pixels)), 4)]

                                                bpy.data.images.remove(copy_img)

                                    if not current_data:
                                        if multi_channel:
                                            current_data = tuple([x for x in bsdf.inputs[input_name].default_value])
                                        else:
                                            current_data = tuple([bsdf.inputs[input_name].default_value for i in range(0, 4)])

                                        current_data = [current_data for x in range(0, total_pixels)]
                                    channel_data[channel] = current_data
                                
                                final_pixels = []
                                
                                for x in range(0, total_pixels):
                                    pixel = [1, 1, 1, 1]
                                    for channel in channel_data.keys():
                                        
                                        channel_pixel = channel_data[channel][x]
                                        if channel == 'RGB':
                                            pixel[0], pixel[1], pixel[2] = channel_pixel[0], channel_pixel[1], channel_pixel[2]
                                        elif channel == 'RGBA':
                                            pixel[0], pixel[1], pixel[2], pixel[3] = channel_pixel[0], channel_pixel[1], channel_pixel[2],channel_pixel[3]
                                        elif channel == 'R':
                                            pixel[0]= channel_pixel[0]
                                        elif channel == 'G':
                                            pixel[1]= channel_pixel[1]
                                        elif channel == 'B':
                                            pixel[2]= channel_pixel[2]
                                        elif channel == 'A':
                                            pixel[3]= channel_pixel[3]
                                        elif channel == 'BW':
                                            pixel[0], pixel[1], pixel[2], pixel[3] = channel_pixel[0], channel_pixel[0], channel_pixel[0],channel_pixel[0]
                                    final_pixels.append(tuple(pixel))
                                
                                pixels = [chan for px in final_pixels for chan in px]
                                
                                final_img = bpy.data.images.new('__export__', min_width, min_height, alpha=True)
                                final_img.pixels = pixels

                                tex_name = mat_slot.material.name + texture_packer.suffix
                                filename = self.file.format(texture_name=tex_name) + file_formats_enum[self.image_format]
                                path = os.path.join(folderpath, filename)

                                bpy.context.scene.render.image_settings.color_mode = ''.join(channels)
                                final_img.save_render(path, scene=bpy.context.scene)

                                bpy.data.images.remove(final_img)


                                
        bpy.context.scene.view_settings.view_transform = view_transform
        bpy.context.scene.render.image_settings.file_format = file_format
        bpy.context.scene.render.image_settings.color_mode = color_mode
        bpy.context.scene.render.image_settings.color_depth = color_depth
        bpy.context.scene.render.image_settings.compression = compression
        bpy.context.scene.render.image_settings.tiff_codec = tiff_codec

        


###
'''
def combine_channels_to_image(target_image, R=None, G=None, B=None, A=None, channel_r=0, channel_g=0, channel_b=0, channel_a=0):
    """combine image channels into RGBA-channels of target image"""

    n = 4
    t = numpy.array(target_image.pixels)
    if R:
        t[0::n] = numpy.array(R.pixels)[channel_r::n]
    if G:
        t[1::n] = numpy.array(G.pixels)[channel_g::n]
    if B:
        t[2::n] = numpy.array(B.pixels)[channel_b::n]
    if A:
        t[3::n] = numpy.array(A.pixels)[channel_a::n]
    target_image.pixels = t
'''