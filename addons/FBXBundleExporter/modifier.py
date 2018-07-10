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

	def execute(self):
		pass

	def draw(self, layout):
		layout.label(text="{}".format(self.label), icon='MODIFIER')

	def print(self):
		print("Modifier '{}'' mode: {}".format(label, mode))
