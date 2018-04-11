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


def export(self):
	print("_____________")


	# Warnings
	if bpy.context.scene.FBXBundleSettings.path == "":
		raise Exception("")
		self.report({'ERROR_INVALID_INPUT'}, "Export path not set" )
		return




	bpy.ops.object.mode_set(mode='OBJECT')

	bundles = objects_organise.get_bundles()

	# Store previous settings
	previous_selection = bpy.context.selected_objects.copy()
	previous_unit_system = bpy.context.scene.unit_settings.system


	bpy.context.scene.unit_settings.system = 'METRIC'	

	path_folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))

	for name,objects in bundles.items():
		pivot = objects_organise.get_pivot(objects).copy()

		path = os.path.join(path_folder, name)
		print("Export {}x = {}".format(len(objects),path))

		# Select objects
		bpy.ops.object.select_all(action="DESELECT")
		for obj in objects:
			obj.select = True
			obj.location-= pivot;

			# X-rotation fix
			bpy.context.scene.objects.active = obj
			bpy.ops.transform.rotate(value = (-math.pi / 2.0), axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
		
		# Export selected as FBX
		bpy.ops.export_scene.fbx(
			filepath=path + ".fbx", 
			use_selection=True, 
			
			axis_forward='-Z', 
			axis_up='Y', 

			object_types={'ARMATURE', 'MESH', 'EMPTY'},

			global_scale =1.00, 
			use_mesh_modifiers=True, 
			mesh_smooth_type='OFF', 
			batch_mode='OFF', 
			use_custom_props=False
		)

		for obj in objects:
			#Restore offset
			obj.location+= pivot;

			# Restore X-rotation fix
			bpy.context.scene.objects.active = obj
			bpy.ops.transform.rotate(value = (+math.pi / 2.0), axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


	# Restore previous settings
	bpy.context.scene.unit_settings.system = previous_unit_system
	
	bpy.ops.object.select_all(action='DESELECT')
	for obj in previous_selection:
		obj.select = True