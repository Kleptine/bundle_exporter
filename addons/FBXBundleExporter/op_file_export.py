import bpy, bmesh
import os
import mathutils
from mathutils import Vector

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_export"
	bl_label = "export"
	bl_description = "Export selected bundles"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		return {'FINISHED'}
