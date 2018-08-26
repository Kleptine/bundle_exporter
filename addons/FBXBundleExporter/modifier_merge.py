import bpy, bmesh
import imp
from mathutils import Vector
from . import objects_organise

from . import modifier
imp.reload(modifier) 

class Settings(modifier.Settings):
	pass
	# active = bpy.props.BoolProperty (
	# 	name="Active",
	# 	default=False
	# )


class Modifier(modifier.Modifier):
	mode = 'MERGE'
	label = "Merge Meshes"
	id = 'merge'
	

	def __init__(self):
		super().__init__()


	# def draw(self, layout):
	# 	super().draw(layout)
	# 	if(self.get("active")):
	# 		layout.label(text="ACTIVE Merge!! !!!!", icon='MODIFIER')


	def process_objects(self, name, objects):

		print("Process modifier merge with {} objects".format(len(objects)))
		# Merge objects into single item
		if not objects_organise.get_objects_animation(objects):
			bpy.ops.object.join()
			bpy.context.object.name = name #assign bundle name
			bpy.context.space_data.cursor_location = Vector((0,0,0))
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			bpy.context.scene.objects.active = objects[-1]

			# Apply rotation
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			
			# Re-assign array
			objects = [bpy.context.object]


		return objects
