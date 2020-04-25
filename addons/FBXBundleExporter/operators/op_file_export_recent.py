import bpy, bmesh
import os
import mathutils
import math

from .. import objects_organise


class BGE_OT_export_recent(bpy.types.Operator):
	bl_idname = "bge.export_recent"
	bl_label = "export recent"
	bl_description = "Re-Export recent exported Bundle again."

	@classmethod
	def poll(cls, context):

		if context.space_data.local_view:
			return False

		if bpy.context.scene.BGE_Settings.path == "":
			return False

		if len(bpy.context.scene.BGE_Settings.recent) <= 0:
			return False

		if len(objects_organise.recent_load_objects()) <= 0:
			return False


		return True

	def execute(self, context):
		export_recent(self)
		return {'FINISHED'}



def export_recent(self):
	objects = objects_organise.recent_load_objects()

	# Warnings
	if len(objects) <= 0:
		raise Exception("")
		self.report({'ERROR_INVALID_INPUT'}, "No previous object selection available" )
		return

	bpy.ops.object.mode_set(mode='OBJECT')

	# Store previous settings
	previous_selection = bpy.context.selected_objects.copy()
	previous_active = bpy.context.scene.objects.active
	previous_unit_system = bpy.context.scene.unit_settings.system
	previous_pivot = bpy.context.space_data.pivot_point
	previous_cursor = bpy.context.scene.cursor.location.copy()



	

	bpy.ops.object.select_all(action="DESELECT")
	for obj in objects:
		for i in range(len(obj.layers)):
			if not obj.layers[i]:
				obj.layers[i] = True
		obj.select_set(True)
	
	bpy.context.scene.objects.active = objects[-1]
	bpy.ops.fbxbundle.file_export()



	# Restore previous settings
	bpy.context.scene.unit_settings.system = previous_unit_system
	bpy.context.space_data.pivot_point = previous_pivot
	bpy.context.scene.cursor.location = previous_cursor
	bpy.context.scene.objects.active = previous_active
	bpy.ops.object.select_all(action='DESELECT')
	for obj in previous_selection:
		obj.select_set(True)
	