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

    def _draw_info(self, layout, modifier_bundle_index):
        pass

    def process(self, bundle_info):
        meshes = bundle_info['meshes']

        if meshes:
            for mesh in meshes:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = mesh
                mesh.select_set(True)

                for modifier in mesh.modifiers:
                    if modifier.type == 'ARMATURE':
                        continue
                    try:
                        bpy.ops.object.modifier_apply(modifier=modifier.name)
                    except RuntimeError as e:
                        obj_name = mesh.get('__orig_name__', mesh.name)
                        mod_name = modifier.name
                        mod_type = modifier.type
                        error_msg = str(e)
                        def draw_error(self, context):
                            self.layout.label(text=f"Object: {obj_name}")
                            self.layout.label(text=f"Modifier: {mod_name} ({mod_type})")
                            self.layout.label(text=f"Error: {error_msg}")
                        bpy.context.window_manager.popup_menu(draw_error, title="Failed to Apply Modifier", icon='ERROR')
                        raise

            #bpy.ops.object.convert(target='MESH')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
