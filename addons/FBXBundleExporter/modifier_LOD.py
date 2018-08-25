import bpy, bmesh
from . import modifier

class Modifier(modifier.Modifier):
	label = "LOD"
	mode = 'LOD'

	def __init__(self):
		super().__init__()
