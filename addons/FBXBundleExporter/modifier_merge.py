import bpy, bmesh
import imp
from . import modifier
imp.reload(modifier) 

class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)


class Modifier(modifier.Modifier):
	mode = 'MERGE'
	label = "Merge"
	settings_id = 'xx'
	

	def __init__(self):
		super().__init__()


	# def register(self):

		# eval(self.settings_path()) = bpy.props.PointerProperty(type=Settings)
		# bpy.types.Scene.FBXBundle_modifier_merge = bpy.props.PointerProperty(type=Settings)


	def process_export(fileName, objects):


		# Merge objects into single item
		# if merge and not objects_organise.get_objects_animation(copies):
		# 	bpy.ops.object.join()
		# 	bpy.context.object.name = name
		# 	bpy.context.space_data.cursor_location = Vector((0,0,0))
		# 	bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

		# 	bpy.context.scene.objects.active = obj

		# 	# Apply rotation
		# 	bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			
		# 	# Re-assign array
		# 	copies = [bpy.context.object]


		pass
