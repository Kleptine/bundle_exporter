import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector


class Modifier:
	mode = 'NONE'
	label = "Modifier"


	def __init__(self):
		print("Create class modifier")
		pass

	
	def draw(self, layout):
		layout.label(text="{}".format(self.label), icon='MODIFIER')


	def print(self):
		print("Modifier '{}'' mode: {}".format(label, mode))


	def process_export(fileName, objects):
		pass


	def process_filename(fileName):
		return fileName
