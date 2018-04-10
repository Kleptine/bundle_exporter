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
		import_files(bpy.context.scene.FBXBundleSettings.path)
		return {'FINISHED'}



def import_files(path):
	# https://blender.stackexchange.com/questions/5064/how-to-batch-import-wavefront-obj-files
	# http://ricardolovelace.com/batch-import-and-export-obj-files-in-blender.html
	path = bpy.path.abspath(path)


	filenames = sorted(os.listdir(path))
	filenames = [name for name in filenames if (name.lower().endswith('.fbx') or name.lower().endswith('.obj') )]


	for name in filenames:
		file_path = os.path.join(path, name)
		extension = (os.path.splitext(file_path)[1])[1:].lower()
		print("- {} = {}".format(extension, file_path))

		# https://docs.blender.org/api/2.78a/bpy.ops.import_scene.html
		if extension == 'fbx':
			bpy.ops.import_scene.fbx(filepath = file_path)
		elif extension == 'obj':
			bpy.ops.import_scene.obj(filepath = file_path)

