import bpy, bmesh
from . import modifier

class Modifier(modifier.Modifier):
	label = "Copy Modifiers"
	mode = 'MODIFIERS'

	def __init__(self):
		super().__init__()
