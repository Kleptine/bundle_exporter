import bpy, bmesh
import os
import mathutils
from mathutils import Vector



def export_objects():
	print("_____________")
	bundles = objects_organise.get_bundles()
	if not os.path.dirname(bpy.data.filepath):
		raise Exception("Blend file is not saved")

	if bpy.context.scene.FBXBundleSettings.path == "":
		raise Exception("Export path not set")

	path_folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))

	for name,objects in bundles.items():
		path = os.path.join(path_folder, name)
		print("Export {}".format(path))
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


def import_objects():
	# https://blender.stackexchange.com/questions/5064/how-to-batch-import-wavefront-obj-files
	# http://ricardolovelace.com/batch-import-and-export-obj-files-in-blender.html
	pass


	