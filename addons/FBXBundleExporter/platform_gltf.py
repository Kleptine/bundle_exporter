import bpy
import bmesh
import operator
import mathutils
import addon_utils

from . import platform

class Platform(platform.Platform):
	extension = 'gltf'


	def __init__(self):
		super().__init__()
		

	def is_valid(self):
		# Plugin available for FLTF?
		mode = bpy.context.scene.FBXBundleSettings.target_platform
		if 'io_scene_gltf2' not in addon_utils.addons_fake_modules:
			return False, "GLTF addon not installed"

		if not addon_utils.check("io_scene_gltf2")[1]:
			return False, "GLTF addon not enabled"

		return True, ""



	# def file_export(self, path):
	# 	print("export {}".format(path))

		# bpy.ops.export_scene.selected(exporter_str="export_scene.glb", use_file_browser=True)
		# bpy.ops.export_scene.gltf()


		

	# def file_import(self, path)
	# 	print("import {}".format(path))

