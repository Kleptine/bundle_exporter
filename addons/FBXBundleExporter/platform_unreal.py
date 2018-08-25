import bpy
import bmesh
import operator
import mathutils

from . import platform

class Platform(platform.Platform):
	label = "Unreal"
	extension = 'fbx'

	def __init__(self):
		super().__init__()
		

	# def file_export(self, path):
	# 	print("export {}".format(path))
		

	# def file_import(self, path)
	# 	print("import {}".format(path))

