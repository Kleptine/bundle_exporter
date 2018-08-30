import bpy, bmesh
import imp

from . import modifier
imp.reload(modifier) 

class Modifier(modifier.Modifier):
	label = "Rename"
	id = 'rename'

	def __init__(self):
		super().__init__()
