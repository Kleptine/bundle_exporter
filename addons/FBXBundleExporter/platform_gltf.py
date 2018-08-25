import bpy
import bmesh
import operator
import mathutils

from . import platform

class Platform(platform.Platform):
	label = "GLTF"
	extension = 'gltf'

	def __init__(self):
		super().__init__()
		

	# def file_export(self, path):
	# 	print("export {}".format(path))

		# bpy.ops.export_scene.selected(exporter_str="export_scene.glb", use_file_browser=True)
		# bpy.ops.export_scene.gltf()


		

	# def file_import(self, path)
	# 	print("import {}".format(path))

