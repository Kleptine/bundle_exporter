import bpy, bmesh
import os
import mathutils
import math

from .. import objects_organise
from . import op_file_export


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

	bpy.ops.object.select_all(action="DESELECT")
	for obj in objects:
		obj.hide_viewport = False
		for i in range(len(obj.users_collection)):
			if obj.users_collection[i].hide_viewport:
				obj.users_collection[i].hide_viewport = False
		obj.select_set(True)
	
	bpy.context.view_layer.objects.active = objects[-1]

	op_file_export.export(self, bpy.context.scene.BGE_Settings.target_platform)