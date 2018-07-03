import bpy, bmesh
import os
import mathutils
from mathutils import Vector


class Modifier:
	label = "Modifier"
	mode = 'NONE'

	def __init__(self):
		pass

	def execute():
		pass

	def print():
		print("Modifier '{}'' mode: {}".format(label, mode))
