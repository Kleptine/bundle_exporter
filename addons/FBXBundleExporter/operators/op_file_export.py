import bpy, bmesh
import os
import mathutils
import math

import pathlib

from .. import objects_organise

from .. import modifiers
from .. import platforms



class BGE_OT_file_export(bpy.types.Operator):
	bl_idname = "bge.file_export"
	bl_label = "export"
	bl_description = "Export selected bundles"

	@classmethod
	def poll(cls, context):

		if context.space_data.local_view:
			return False
		
		if len(bpy.context.selected_objects) == 0:
			return False

		if bpy.context.scene.BGE_Settings.path == "":
			return False

		if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.mode != 'OBJECT':
			return False

		if len( objects_organise.get_bundles() ) == 0:
			return False


		return True

	def execute(self, context):
		export(self, bpy.context.scene.BGE_Settings.target_platform)
		return {'FINISHED'}


prefix_copy = "EXPORT_ORG_"

def export(self, target_platform):

	# Warnings
	if bpy.context.scene.BGE_Settings.path == "":
		self.report({'ERROR_INVALID_INPUT'}, "Export path not set" )
		return

	folder = bpy.path.abspath( bpy.context.scene.BGE_Settings.path)
	if not os.path.exists(folder):
		self.report({'ERROR_INVALID_INPUT'}, "Path doesn't exist" )
		return

	if len(bpy.context.selected_objects) == 0 and not bpy.context.view_layer.objects.active:
		self.report({'ERROR_INVALID_INPUT'}, "No objects selected" )
		return

	# Is Mode available?
	mode = bpy.context.scene.BGE_Settings.target_platform
	if mode not in platforms.platforms:
		self.report({'ERROR_INVALID_INPUT'}, "Platform '{}' not supported".format(mode) )
		return

	# Does the platform throw errors?
	if not platforms.platforms[mode].is_valid()[0]:
		self.report({'ERROR_INVALID_INPUT'}, platforms.platforms[mode].is_valid()[1] )
		return			


	# Store previous settings
	previous_selection = bpy.context.selected_objects.copy()
	previous_active = bpy.context.view_layer.objects.active
	previous_unit_system = bpy.context.scene.unit_settings.system
	previous_pivot = bpy.context.scene.tool_settings.transform_pivot_point
	previous_cursor = bpy.context.scene.cursor.location

	if not bpy.context.view_layer.objects.active:
		bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

	bpy.ops.object.mode_set(mode='OBJECT')
	bundles = objects_organise.get_bundles()

	



	bpy.context.scene.unit_settings.system = 'METRIC'	
	bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'


	objects_organise.recent_store(bundles)

	for name,data in bundles.items():
		objects = data['objects']
		helpers = data['helpers']
		all_data = objects + helpers

		pivot = objects_organise.get_pivot(all_data).copy()

		# Detect if animation export...
		use_animation = objects_organise.get_objects_animation(objects)

		def copy_object(obj, convert = True):
			name_original = obj.name
			obj.name = prefix_copy+name_original

			bpy.ops.object.select_all(action="DESELECT")
			obj.select_set(True)
			bpy.context.view_layer.objects.active = obj
			obj.hide_viewport = False
			#bpy.context.view_layer.update()
			
			# Copy
			bpy.ops.object.duplicate()
			if convert:
				bpy.ops.object.convert(target='MESH')
			bpy.context.object.name = name_original
			
			bpy.context.object.location-= pivot

			return bpy.context.object

		copies = []
		for obj in objects:
			copies.append(copy_object(obj))

		for helper in helpers:
			copied_helper = copy_object(helper, convert = False)
			copied_helper.scale[0]*= 0.01
			copied_helper.scale[1]*= 0.01
			copied_helper.scale[2]*= 0.01

			copies.append(copied_helper)


		bpy.ops.object.select_all(action="DESELECT")
		for obj in copies:
			obj.select_set(True)
		bpy.context.view_layer.objects.active = copies[0]


		# Apply modifiers

		# full = self.process_path(name, path)+"{}".format(os.path.sep)+platforms.platforms[mode].get_filename( self.process_name(name) )  		
		# os.path.join(folder, name)+"."+platforms.platforms[mode].extension
		path_folder = folder
		path_name = name
		for modifier in modifiers.modifiers:
			if modifier.get("active"):
				copies = modifier.process_objects(name, copies)
				path_folder = modifier.process_path(path_name, path_folder)
				path_name = modifier.process_name(path_name)

		path_full = os.path.join(path_folder, path_name)+"."+platforms.platforms[mode].extension
		
		# Create path if not yet available
		directory = os.path.dirname(path_full)
		pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

		# Select all copies
		bpy.ops.object.select_all(action="DESELECT")
		for obj in copies:
			obj.select_set(True)

		# Export per platform (Unreal, Unity, ...)
		print("Export {}x = {}".format(len(objects),path_full))
		platforms.platforms[mode].file_export(path_full)

		# Delete copies
		bpy.ops.object.delete()
		copies.clear()
		
		# Restore names
		for obj in all_data:
			obj.name = obj.name.replace(prefix_copy,"")

		


	# Restore previous settings
	bpy.context.scene.unit_settings.system = previous_unit_system
	bpy.context.scene.tool_settings.transform_pivot_point = previous_pivot
	bpy.context.scene.cursor.location = previous_cursor
	bpy.context.view_layer.objects.active = previous_active
	bpy.ops.object.select_all(action='DESELECT')
	for obj in previous_selection:
		obj.select_set(True)

	# Show popup
	
	def draw(self, context):
		filenames = []
		# Get bundle file names
		for name,data in bundles.items():
			for modifier in modifiers.modifiers:
				if modifier.get("active"):
					name = modifier.process_name(name)	
			filenames.append(name+"."+platforms.platforms[mode].extension)

		self.layout.label(text="Exported:")
		for x in filenames:
			self.layout.label(text=x)

		self.layout.operator("wm.path_open", text=folder, icon='FILE_FOLDER').filepath = folder

	bpy.context.window_manager.popup_menu(draw, title = "Exported {}x files".format(len(bundles)), icon = 'INFO')
	