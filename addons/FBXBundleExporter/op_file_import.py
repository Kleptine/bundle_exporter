import bpy, bmesh
import os
import mathutils
from mathutils import Vector

from . import objects_organise

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_import"
	bl_label = "Import"
	bl_description = "Import multiple objects"

	@classmethod
	def poll(cls, context):
		if bpy.context.scene.FBXBundleSettings.path == "":
			return False
			
		return True

	def execute(self, context):
		import_files()
		return {'FINISHED'}



def import_files():
	# https://blender.stackexchange.com/questions/5064/how-to-batch-import-wavefront-obj-files
	# http://ricardolovelace.com/batch-import-and-export-obj-files-in-blender.html
	pass