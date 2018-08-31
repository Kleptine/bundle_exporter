import bpy, bmesh
import math
import imp

from . import modifier
imp.reload(modifier) 




class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)


class Modifier(modifier.Modifier):
	label = "Vertex AO"
	id = 'vertex_ao'


	def __init__(self):
		super().__init__()

	def process_objects(self, name, objects):
		
		for obj in objects:
			bpy.ops.object.select_all(action="DESELECT")
			obj.select = True
			bpy.context.scene.objects.active = obj

			# Set AO vertex colors
			bpy.ops.object.mode_set(mode='VERTEX_PAINT')
			bpy.ops.paint.vertex_color_set()
			bpy.ops.paint.vertex_color_dirt()

			# Back to object mode
			bpy.ops.object.mode_set(mode='OBJECT')

		return objects