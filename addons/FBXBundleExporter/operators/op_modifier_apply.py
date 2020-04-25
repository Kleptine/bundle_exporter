import bpy, bmesh
import os
import mathutils


from .. import objects_organise

from .. import modifiers




class BGE_OT_modifier_apply(bpy.types.Operator):
	bl_idname = "bge.modifier_apply"
	bl_label = "Apply"
	bl_description = "Apply this modifier now"
	bl_options = {'REGISTER', 'UNDO'}

	modifier_index: bpy.props.IntProperty (
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

		if self.modifier_index < len(modifiers.modifiers):
			bundles = objects_organise.get_bundles()

			if(len(bundles) > 0):
				for fileName,objects in bundles.items():

					bpy.ops.object.select_all(action="DESELECT")
					for obj in objects:
						obj.select_set(True)
					bpy.context.scene.objects.active = objects[0]

					modifiers.modifiers[self.modifier_index].process_objects(fileName, objects)

					
		bpy.context.scene.update()
		return {'FINISHED'}
