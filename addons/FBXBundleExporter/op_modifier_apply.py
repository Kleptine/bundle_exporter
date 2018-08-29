import bpy, bmesh
import os
import mathutils
import imp

from . import objects_organise
imp.reload(objects_organise)

from . import modifiers
imp.reload(modifiers)




class op(bpy.types.Operator):
	bl_idname = "fbxbundle.modifier_apply"
	bl_label = "Apply"
	bl_description = "Apply this modifier now"

	modifier_index = bpy.props.IntProperty (
		default=0
	)

	@classmethod
	def poll(cls, context):
		if not context.active_object:
			return False
		if len(bpy.context.selected_objects) <= 0:
			return False

		return True


	def execute(self, context):
		print("Execute Apply modifier '{}'".format(self.modifier_index))

		if self.modifier_index < len(modifiers.modifiers):
			print("Yes index valid")


			bundles = objects_organise.get_bundles()

			if(len(bundles) > 0):
				for fileName,objects in bundles.items():

					bpy.ops.object.select_all(action="DESELECT")
					for obj in objects:
						obj.select = True
					bpy.context.scene.objects.active = objects[0]

					print("Apply modifier to set {} ".format(fileName))
					modifiers.modifiers[self.modifier_index].process_objects(fileName, objects)

		return {'FINISHED'}
