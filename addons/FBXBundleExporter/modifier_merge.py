import bpy, bmesh
import imp
from mathutils import Vector
from . import objects_organise

from . import modifier
imp.reload(modifier) 

class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	merge_active = bpy.props.BoolProperty (
		name="Merge",
		default=False
	)
	merge_distance = bpy.props.FloatProperty (
		name="Merge Verts",
		default=0,
		min = 0,
		description="Minimum distance of verts to merge. Set to 0 to disable.",
		subtype='DISTANCE'
	)


class Modifier(modifier.Modifier):
	mode = 'MERGE'
	label = "Merge Meshes"
	id = 'merge'
	
	def __init__(self):
		super().__init__()


	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			row = layout.row()
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_active", text="", icon='AUTOMERGE_ON')
			row_freeze = row.row()
			row_freeze.enabled = self.get("merge_active")
			row_freeze.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_distance")


	def process_objects(self, name, objects):

		# Merge objects into single item
		if not objects_organise.get_objects_animation(objects):
			bpy.ops.object.join()
			bpy.context.object.name = name #assign bundle name
			bpy.context.space_data.cursor_location = Vector((0,0,0))
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			# bpy.context.scene.objects.active = objects[-1]

			# Apply rotation
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			

			# Merge Vertices?
			if(self.get("merge_active") and self.get("merge_distance") > 0):

				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
				bpy.ops.mesh.select_all(action='SELECT')

				bpy.ops.mesh.remove_doubles(threshold = self.get("merge_distance"))

				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

			# Re-assign array
			objects = [bpy.context.object]


		return objects
