import bpy, bmesh
import os
import mathutils
import math

class BGE_OT_export_recent_clear(bpy.types.Operator):
	bl_idname = "bge.export_recent_clear"
	bl_label = "Clear recent"
	bl_description = "Clear recent Re-Export."

	@classmethod
	def poll(cls, context):

		if len(bpy.context.scene.BGE_Settings.recent) == 0:
			return False

		return True

	def execute(self, context):
		bpy.context.scene.BGE_Settings.recent = ""
		return {'FINISHED'}
