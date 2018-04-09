import bpy, bmesh
import os
import mathutils
from mathutils import Vector

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_import"
	bl_label = "Import"
	bl_description = "Import multiple objects"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		return {'FINISHED'}
