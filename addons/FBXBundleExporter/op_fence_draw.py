import bpy, bmesh
import os
import mathutils
from mathutils import Vector

from . import objects_organise
from . import gp_draw

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.fence_draw"
	bl_label = "Draw Fences"
	bl_description = "Draw fences around selected bundles"

	@classmethod
	def poll(cls, context):
		if len(bpy.context.selected_objects) > 0:
			return True
		return False

	def execute(self, context):

		gp_draw.clear()

		bundles = objects_organise.get_bundles()
		for name,objects in bundles.items():
			if len(objects) > 0:
				bounds = objects_organise.ObjectBounds(objects[0])
				if len(objects) > 1:
					for i in range(1,len(objects)):
						bounds.combine( objects_organise.ObjectBounds(objects[i]) )

				gp_draw.draw_bounds(name, objects, bounds)

		return {'FINISHED'}
