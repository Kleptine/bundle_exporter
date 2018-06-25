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

		if len( objects_organise.get_bundles() ) == 0:
			return False


		return True

	def execute(self, context):
		export(self, bpy.context.scene.FBXBundleSettings.target_platform)
		return {'FINISHED'}


prefix_copy = "EXPORT_ORG_"

def export(self, target_platform):

	# Warnings
	if bpy.context.scene.FBXBundleSettings.path == "":
		raise Exception("")
		self.report({'ERROR_INVALID_INPUT'}, "Export path not set" )
		return

	path_folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))
	if not os.path.exists(path_folder):
		self.report({'ERROR_INVALID_INPUT'}, "Path doesn't exist" )
		return


	bpy.ops.object.mode_set(mode='OBJECT')

	merge = bpy.context.scene.FBXBundleSettings.merge
	bundles = objects_organise.get_bundles()

	# Store previous settings
	previous_selection = bpy.context.selected_objects.copy()
	previous_active = bpy.context.scene.objects.active
	previous_unit_system = bpy.context.scene.unit_settings.system
	previous_pivot = bpy.context.space_data.pivot_point
	previous_cursor = bpy.context.space_data.cursor_location.copy()

	bpy.context.scene.unit_settings.system = 'METRIC'	
	bpy.context.space_data.pivot_point = 'MEDIAN_POINT'

	for name,objects in bundles.items():
		pivot = objects_organise.get_pivot(objects).copy()

		path = os.path.join(path_folder, name)
		print("Export {}x = {}".format(len(objects),path))

		copies = []
		for obj in objects:
			name_original = obj.name
			obj.name = prefix_copy+name_original

			bpy.ops.object.select_all(action="DESELECT")
			obj.select = True
			bpy.context.scene.objects.active = obj

			# Copy
			bpy.ops.object.duplicate()
			bpy.ops.object.convert(target='MESH')
			bpy.context.object.name = name_original
			copies.append(bpy.context.object)
			
			bpy.context.object.location-= pivot;

			# Rotation
			if not merge:
				transform_target_platform(bpy.context.object, target_platform)


		bpy.ops.object.select_all(action="DESELECT")
		for obj in copies:
			obj.select = True


		if merge:
			# Merge objects into single item

			bpy.ops.object.join()
			bpy.context.object.name = name
			bpy.context.space_data.cursor_location = Vector((0,0,0))
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			transform_target_platform(bpy.context.object, target_platform)

			copies = [bpy.context.object]


		# Axis vectors for different platforms
		axis_forward, axis_up = 'Y', 'Z' #Default
		if target_platform == 'UNITY':
			axis_forward = '-Z'
			axis_up = 'Y'

		# Export selected as FBX
		scale_options = 'FBX_SCALE_ALL'
		
		if target_platform == 'UNREAL':
			scale_options = 'FBX_SCALE_NONE'
		elif target_platform == 'UNITY':
			scale_options = 'FBX_SCALE_ALL'



		bpy.ops.export_scene.fbx(
			filepath=path + ".fbx", 
			use_selection=True, 
			
			axis_forward=axis_forward, 
			axis_up=axis_up, 

			object_types={'ARMATURE', 'MESH', 'EMPTY'},

			apply_scale_options = scale_options,
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


	# Restore previous settings
	bpy.context.scene.unit_settings.system = previous_unit_system
	bpy.context.space_data.pivot_point = previous_pivot
	bpy.context.space_data.cursor_location = previous_cursor
	bpy.context.scene.objects.active = previous_active
	bpy.ops.object.select_all(action='DESELECT')
	for obj in previous_selection:
		obj.select = True




def transform_target_platform(obj, target_platform):
	bpy.context.scene.objects.active = obj

	if target_platform == 'UNITY':
		# Apply -90 degrees rotation offset
		bpy.ops.transform.rotate(value = (-math.pi / 2.0), axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)