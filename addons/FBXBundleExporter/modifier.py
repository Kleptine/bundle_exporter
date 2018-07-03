import bpy, bmesh
import os
import mathutils
from mathutils import Vector


class Modifier:
	label = ""					#Material name from external blend file
	mode = 'EMIT'

	def __init__(self, label="", mode='EMIT'):
		self.label = label
		self.mode = mode
