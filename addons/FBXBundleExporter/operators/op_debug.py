import bpy

from .. import gp_draw


class BGE_PT_debug_lines(bpy.types.Operator):
	bl_idname = "bge.debug_lines"
	bl_label = "Debug"

	def execute(self, context):
		print ("Debug Operator")

		gp_draw.draw_debug()

		return {'FINISHED'}


class BGE_PT_debug_setup(bpy.types.Operator):
	bl_idname = "bge.debug_setup"
	bl_label = "Setup"

	def execute(self, context):
		print ("Debug Setup Operator")

		# Disable grid
		bpy.context.space_data.overlay.show_axis_x = not bpy.context.space_data.overlay.show_axis_x
		bpy.context.space_data.overlay.show_axis_y = not bpy.context.space_data.overlay.show_axis_y
		bpy.context.space_data.overlay.show_axis_z = not bpy.context.space_data.overlay.show_axis_z
		bpy.context.space_data.overlay.grid_lines = 6
		bpy.context.space_data.overlay.grid_subdivisions = 1
		bpy.context.space_data.overlay.grid_scale = 0.1
		bpy.context.space_data.overlay.show_floor = not bpy.context.space_data.overlay.show_floor

		bpy.context.space_data.overlay.show_object_origins_all = True


		return {'FINISHED'}
