import bpy, bmesh
import os
import mathutils
import math

import pathlib

from .. import objects_organise

from .. import modifiers
from .. import platforms
from .. import bundles

prefix_copy = "EXPORT_ORG_"

class BGE_OT_file_export(bpy.types.Operator):
	bl_idname = "bge.file_export"
	bl_label = "export"
	bl_description = "Export Bundles"

	@classmethod
	def poll(cls, context):
		if context.space_data.local_view:
			return False

		if bpy.context.scene.BGE_Settings.path == "":
			return False

		if len(bpy.context.scene.BGE_Settings.bundles) == 0:
			return False

		return True

	def execute(self, context):
		# Warnings
		if bpy.context.scene.BGE_Settings.path == "":
			self.report({'ERROR_INVALID_INPUT'}, "Export path not set" )
			return

		folder = bpy.path.abspath( bpy.context.scene.BGE_Settings.path)
		if not os.path.exists(folder):
			self.report({'ERROR_INVALID_INPUT'}, "Path doesn't exist" )
			return

		if len(bpy.context.scene.BGE_Settings.bundles) == 0:
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

		bundles.exporter.export(bundles.get_bundles(),  bpy.context.scene.BGE_Settings.path, bpy.context.scene.BGE_Settings.target_platform)

		return {'FINISHED'}
