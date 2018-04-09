import bpy, bmesh
import os
import mathutils
from mathutils import Vector

from . import objects_organise

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_export"
	bl_label = "export"
	bl_description = "Export selected bundles"

	@classmethod
	def poll(cls, context):
		if len(bpy.context.selected_objects) == 0:
			return False

		if bpy.context.scene.FBXBundleSettings.path == "":
			return False

		return True

	def execute(self, context):
		export(self)
		return {'FINISHED'}


def export(self):
	print("_____________")
	bpy.ops.object.mode_set(mode='OBJECT')

	bundles = objects_organise.get_bundles()
	selected_obj = bpy.context.selected_objects.copy()

	# if not os.path.dirname(bpy.data.filepath):
		# raise Exception("Blend file is not saved")

	if bpy.context.scene.FBXBundleSettings.path == "":
		raise Exception("")
		self.report({'ERROR_INVALID_INPUT'}, "Export path not set" )
		return

	path_folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))

	for name,objects in bundles.items():
		path = os.path.join(path_folder, name)
		print("Export {}x = {}".format(len(objects),path))

		bpy.ops.object.select_all(action="DESELECT")
		for obj in objects:
			obj.select = True



		# # offset
		# offset = objects[0].location.copy();
		
		# # Select Group
		# for object in objects:
		# 	object.select = True
		# 	object.location =  object.location.copy() - offset;#

		# #Export
		# path = os.path.join(dir, fileName)
		# export_FBX(path)

		# #Restore offset
		# for object in objects:
		# 	object.location=object.location + offset;

	# restore mode
	
	bpy.ops.object.select_all(action='DESELECT')
	for obj in selected_obj:
		obj.select = True