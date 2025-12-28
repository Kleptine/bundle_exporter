import bpy
op = bpy.context.active_operator

op.export_selected_objects = True
op.export_animation = False
op.apply_modifiers = True
op.export_smooth_groups = True
op.smooth_group_bitflags = False
op.export_normals = True
op.export_uv = True
op.export_materials = False
op.export_triangulated_mesh = True
op.export_curves_as_nurbs = False
op.export_vertex_groups = False
op.export_object_groups = True
op.export_material_groups = False
op.global_scale = 1.0
op.path_mode = 'AUTO'
op.forward_axis = 'NEGATIVE_Z'
op.up_axis = 'Y'
