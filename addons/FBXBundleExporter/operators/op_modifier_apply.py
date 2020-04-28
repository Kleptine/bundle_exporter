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

	modifier_id: bpy.props.StringProperty (
		default="DEFAULT"
	)

	@classmethod
	def poll(cls, context):
		if not context.active_object:
			return False
		if len(bpy.context.selected_objects) <= 0:
			return False

		return True


	def execute(self, context):
		modifier_ids = [x.id for x in modifiers.modifiers_dict]

		if self.modifier_id in modifier_ids:
			bundles = objects_organise.get_bundles()

			if(len(bundles) > 0):
				for fileName,data in bundles.items():
					objects = data['objects']

					bpy.ops.object.select_all(action="DESELECT")
					for obj in objects:
						obj.select_set(True)
					bpy.context.view_layer.objects.active = objects[0]

					modifiers.modifiers_dict[self.modifier_id]['modifier'].process_objects(fileName, objects)

					
		bpy.context.scene.update()
		return {'FINISHED'}
