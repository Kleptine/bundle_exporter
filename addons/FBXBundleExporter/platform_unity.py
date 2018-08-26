import bpy
import bmesh
import operator
import mathutils

from . import platform

class Platform(platform.Platform):
	extension = 'fbx'


	def __init__(self):
		super().__init__()


	def is_valid(self):
		if bpy.context.scene.unit_settings.system != 'METRIC':
			return False, "Scene units not metric"
		return True, ""


	# def file_export(self, path):
	# 	print("export {}".format(path))
		

	# def file_import(self, path)
	# 	print("import {}".format(path))

