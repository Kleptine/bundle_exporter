import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import operator

from . import objects_organise
from . import gp_draw



class op(bpy.types.Operator):
	bl_idname = "fbxbundle.fix_geometry"
	bl_label = "Fix Geometry"
	bl_description = "Remove custom splitnormals, consistent normals" #, fix humongus UV coordinates

	def execute(self, context):
		print ("Fix Geometry")

		bpy.ops.object.mode_set(mode='OBJECT')

		objects = bpy.context.selected_objects
		for obj in objects:
			if obj.type == 'MESH':
				# Select object
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action="DESELECT")
				obj.select = True

				# Clear custom normals data
				bpy.ops.mesh.customdata_custom_splitnormals_clear()

				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.remove_doubles()

				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
				bpy.ops.mesh.normals_make_consistent(inside=False)

				# bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
				# bpy.ops.mesh.mark_sharp(clear=True)

				bpy.ops.mesh.select_all(action='DESELECT')
			
		# Restore selection
		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.ops.object.select_all(action="DESELECT")
		for obj in objects:
			obj.select = True

		return {'FINISHED'}

