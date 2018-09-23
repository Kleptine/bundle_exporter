import bpy, bmesh
import os
import mathutils
import math
import imp
from . import objects_organise

from . import modifiers
from . import platforms

imp.reload(modifiers)
imp.reload(platforms)


class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_export"
	bl_label = "export"
	bl_description = "Export selected bundles"

	@classmethod
	def poll(cls, context):

		if context.space_data.local_view:
			return False
		
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

	if len(bpy.context.selected_objects) == 0 and not bpy.context.scene.objects.active:
		self.report({'ERROR_INVALID_INPUT'}, "No objects selected" )
		return

	# Is Mode available?
	mode = bpy.context.scene.FBXBundleSettings.target_platform
	if mode not in platforms.platforms:
		self.report({'ERROR_INVALID_INPUT'}, "Platform '{}' not supported".format(mode) )
		return

	# Does the platform throw errors?
	if not platforms.platforms[mode].is_valid()[0]:
		self.report({'ERROR_INVALID_INPUT'}, platforms.platforms[mode].is_valid()[1] )
		return			


	# Store previous settings
	previous_selection = bpy.context.selected_objects.copy()
	previous_active = bpy.context.scene.objects.active
	previous_unit_system = bpy.context.scene.unit_settings.system
	previous_pivot = bpy.context.space_data.pivot_point
	previous_cursor = bpy.context.space_data.cursor_location.copy()

	if not bpy.context.scene.objects.active:
		bpy.context.scene.objects.active = bpy.context.selected_objects[0]

	bpy.ops.object.mode_set(mode='OBJECT')
	bundles = objects_organise.get_bundles()

	



	bpy.context.scene.unit_settings.system = 'METRIC'	
	bpy.context.space_data.pivot_point = 'MEDIAN_POINT'

	objects_organise.recent_store(bundles)

	for name,objects in bundles.items():
		pivot = objects_organise.get_pivot(objects).copy()

		path = os.path.join(path_folder, name)+"."+platforms.platforms[mode].extension

		print("Export {}x = {}".format(len(objects),path))


		# Detect if animation export...
		use_animation = objects_organise.get_objects_animation(objects)


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
			
			bpy.context.object.location-= pivot


		bpy.ops.object.select_all(action="DESELECT")
		for obj in copies:
			obj.select = True
		bpy.context.scene.objects.active = copies[0]

		# ...apply modifiers
		for modifier in modifiers.modifiers:
			if modifier.get("active"):
				copies = modifier.process_objects(name, copies)

		# Select all copies
		bpy.ops.object.select_all(action="DESELECT")
		for obj in copies:
			obj.select = True

		# Export per platform (Unreal, Unity, ...)
		platforms.platforms[mode].file_export(path)

		# Delete copies
		
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
	