import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector


class Platform:
	label = "Platform"
	extension = 'fbx'

	def __init__(self):
		print("Create platform")


	def get_filename(self, filename):
		return "{}.{}".format(filename, self.extension)


	def is_valid(self):
		return True, ""


	def file_export(self, path):
		print("{} export {}".format(self.label, path))
		

	# def file_import(self, path):
	# 	print("{} import {}".format(self.label, path))

