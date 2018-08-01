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
	bl_description = "Remove custom splitnormals, consistent normals, fix exceeding > 8 UV coordinates"

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

				# Remove doubles
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.remove_doubles()

				# Recalculate Normals
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
				bpy.ops.mesh.normals_make_consistent(inside=False)

				#Limit UV's to not exceed a value
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				uv_layer = bm.loops.layers.uv.verify()
				
				limit = 8.00
				for face in bm.faces:
					for loop in face.loops:
						uv = loop[uv_layer].uv
						if(abs(uv.x) > limit):
							uv.x = limit * abs(uv.x)/uv.x
						if(abs(uv.y) > limit):
							uv.y = limit * abs(uv.y)/uv.y

				bpy.ops.mesh.select_all(action='DESELECT')
			
		# Restore selection
		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.ops.object.select_all(action="DESELECT")
		for obj in objects:
			obj.select = True

		return {'FINISHED'}

