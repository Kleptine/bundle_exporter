import bpy, bmesh
from . import modifier

class Modifier(modifier.Modifier):
	label = "Collider"
	mode = 'COLLIDER'

	def __init__(self):
		super().__init__()
