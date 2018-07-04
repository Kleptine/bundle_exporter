import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector


class Modifier:
	label = "Modifier"
	mode = 'NONE'

	def __init__(self):
		print("Create class modifier")
		pass

	def execute():
		pass

	def print():
		print("Modifier '{}'' mode: {}".format(label, mode))
