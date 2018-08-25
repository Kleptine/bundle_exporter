import bpy, bmesh
from . import modifier

class Modifier(modifier.Modifier):
	label = "Rename"
	mode = 'RENAME'

	def __init__(self):
		super().__init__()
