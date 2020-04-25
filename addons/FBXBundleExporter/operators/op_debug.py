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
		bpy.context.space_data.show_axis_x = False
		bpy.context.space_data.show_axis_y = False
		bpy.context.space_data.show_axis_z = False
		bpy.context.space_data.grid_lines = 6
		bpy.context.space_data.grid_subdivisions = 1
		bpy.context.space_data.grid_scale = 1
		bpy.context.space_data.show_floor = False

		bpy.context.space_data.show_all_objects_origin = True


		return {'FINISHED'}
