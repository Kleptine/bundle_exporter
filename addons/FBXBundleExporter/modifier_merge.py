import bpy, bmesh
import os
import mathutils
from mathutils import Vector


from . import modifier

class Modifier(modifier.Modifier):
	label = "Merge"
	mode = 'MERGE'

	def __init__(self):
		super().__init__()
