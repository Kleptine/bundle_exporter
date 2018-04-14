import bpy, bmesh
import os
import mathutils
import math
from mathutils import Vector

from . import objects_organise

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_export"
	bl_label = "export"
	bl_description = "Export selected bundles"

	@classmethod
	def poll(cls, context):
		if len(bpy.context.selected_objects) == 0:
			return False

		if bpy.context.scene.FBXBundleSettings.path == "":
			return False

		if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
			return False

		return True

	def execute(self, context):
		export(self)
		return {'FINISHED'}


prefix_copy = "EXPORT_ORG_"

def export(self):
	print("_____________")


	# Warnings
	if bpy.context.scene.FBXBundleSettings.path == "":
		raise Exception("")
		self.report({'ERROR_INVALID_INPUT'}, "Export path not set" )
		return




	bpy.ops.object.mode_set(mode='OBJECT')

	merge = bpy.context.scene.FBXBundleSettings.merge
	bundles = objects_organise.get_bundles()

	# Store previous settings
	previous_selection = bpy.context.selected_objects.copy()
	previous_unit_system = bpy.context.scene.unit_settings.system
	previous_pivot = bpy.context.space_data.pivot_point
	previous_cursor = bpy.context.space_data.cursor_location.copy()



	bpy.context.scene.unit_settings.system = 'METRIC'	
	bpy.context.space_data.pivot_point = 'MEDIAN_POINT'



	path_folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))

	for name,objects in bundles.items():
		pivot = objects_organise.get_pivot(objects).copy()

		path = os.path.join(path_folder, name)
		print("Export {}x = {}".format(len(objects),path))

		copies = []
		for obj in objects:
			name = obj.name
			obj.name = prefix_copy+name

			bpy.ops.object.select_all(action="DESELECT")
			obj.select = True
			bpy.context.scene.objects.active = obj

			# Copy
			bpy.ops.object.duplicate()
			bpy.ops.object.convert(target='MESH')
			bpy.context.object.name = name
			copies.append(bpy.context.object)
			bpy.context.scene.objects.active = bpy.context.object

			# Offset
			bpy.context.object.location-= pivot;

			# Rotation
			if not merge:
				bpy.ops.transform.rotate(value = (-math.pi / 2.0), axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)



		bpy.ops.object.select_all(action="DESELECT")
		for obj in copies:
			obj.select = True


		if merge:
			# Merge objects into single item
			bpy.ops.object.join()
			bpy.context.space_data.cursor_location = Vector((0,0,0))
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			bpy.ops.transform.rotate(value = (-math.pi / 2.0), axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
		
			copies = [bpy.context.scene.objects.active]




		# Export selected as FBX
		bpy.ops.export_scene.fbx(
			filepath=path + ".fbx", 
			use_selection=True, 
			
			axis_forward='-Z', 
			axis_up='Y', 

			object_types={'ARMATURE', 'MESH', 'EMPTY'},

			apply_scale_options = 'FBX_SCALE_ALL',
			global_scale =1.00, 
			apply_unit_scale=True,

			use_mesh_modifiers=True, 
			mesh_smooth_type='OFF', 
			batch_mode='OFF', 
			use_custom_props=False
		)

		bpy.ops.object.delete()
		copies.clear()
		
		# Restore names
		for obj in objects:
			obj.name = obj.name.replace(prefix_copy,"")



		'''
		# Apply Transforms
		for obj in objects:
			bpy.ops.object.select_all(action="DESELECT")
			obj.select = True
			bpy.context.scene.objects.active = obj
			
			# Offset
			obj.location-= pivot;
			
			# X-rotation fix
			bpy.ops.transform.rotate(value = (-math.pi / 2.0), axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			

		# Select objects
		bpy.ops.object.select_all(action="DESELECT")
		for obj in objects:
			obj.select = True


		

		# Restore transforms
		for obj in objects:
			bpy.ops.object.select_all(action="DESELECT")
			obj.select = True
			bpy.context.scene.objects.active = obj

			#Restore offset
			obj.location+= pivot;

			# Restore X-rotation fix
			bpy.ops.transform.rotate(value = (+math.pi / 2.0), axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			
		'''
	# Restore previous settings
	bpy.context.scene.unit_settings.system = previous_unit_system
	bpy.context.space_data.pivot_point = previous_pivot
	bpy.context.space_data.cursor_location = previous_cursor

	bpy.ops.object.select_all(action='DESELECT')
	for obj in previous_selection:
		obj.select = True