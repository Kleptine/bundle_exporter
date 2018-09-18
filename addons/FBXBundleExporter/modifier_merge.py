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
	merge_verts = bpy.props.BoolProperty (
		name="Merge",
		default=False
	)
	merge_by_material = bpy.props.BoolProperty (
		name="By Material",
		default=False
	)

	merge_distance = bpy.props.FloatProperty (
		name="Dist.",
		default=0,
		min = 0,
		description="Minimum distance of verts to merge. Set to 0 to disable.",
		subtype='DISTANCE'
	)
	consistent_normals = bpy.props.BoolProperty (
		name="Make consistent Normals",
		default=True
	)



class Modifier(modifier.Modifier):
	label = "Merge Meshes"
	id = 'merge'
	
	def __init__(self):
		super().__init__()


	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			col = layout.column(align=True)

			row = col.row(align=True)
			row.separator()
			row.separator()
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_verts", text="Merge Verts")
			row_freeze = row.row()
			row_freeze.enabled = self.get("merge_verts")
			row_freeze.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_distance")

			row = col.row(align=True)
			row.separator()
			row.separator()
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "consistent_normals", text="Consistent Normals")

			row = col.row(align=True)
			row.separator()
			row.separator()
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_by_material", text="Merge by Material")


			
			


	def process_objects(self, name, objects):

		# Merge objects into single item
		if not objects_organise.get_objects_animation(objects):
			bpy.ops.object.join()
			bpy.context.object.name = name #assign bundle name
			bpy.context.space_data.cursor_location = Vector((0,0,0))
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			# bpy.context.scene.objects.active = objects[-1]

			# Convert to mesh
			bpy.ops.object.convert(target='MESH')


			# Apply rotation
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			

			# Merge Vertices?
			if self.get("merge_verts") and self.get("merge_distance") > 0:

				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
				bpy.ops.mesh.select_all(action='SELECT')

				bpy.ops.mesh.remove_doubles(threshold = self.get("merge_distance"))

				bpy.ops.mesh.quads_convert_to_tris()

				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

			
			if self.get("consistent_normals") :
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
				bpy.ops.mesh.select_all(action='SELECT')

				bpy.ops.mesh.normals_make_consistent(inside=False)

				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')


			if self.get("merge_by_material") :
				# TODO: Split faces by materials
				pass

			# Re-assign array
			objects = [bpy.context.object]


		return objects
