import bpy, bmesh
from . import modifier

class Settings(bpy.types.PropertyGroup):
	merge = bpy.props.BoolProperty (
		name="Active",
		default=False,
		description="Enable Modifier"
	)


class Modifier(modifier.Modifier):
	label = "Merge"
	mode = 'MERGE'


	def __init__(self):
		super().__init__()


	def process_export(fileName, objects):
		pass
