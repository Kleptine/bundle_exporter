import bpy

from .. import objects_organise

class BGE_OT_select(bpy.types.Operator):
	bl_idname = "bge.select"
	bl_label = "Select"

	key: bpy.props.StringProperty (name="Key")
	def execute(self, context):
		bundles = objects_organise.get_bundles()
		if self.key in bundles:
			bpy.ops.object.select_all(action='DESELECT')
			for obj in bundles[self.key]['objects']:
				obj.select_set(True)
		return {'FINISHED'}



class BGE_OT_remove(bpy.types.Operator):
	bl_idname = "bge.remove"
	bl_label = "Remove"

	key: bpy.props.StringProperty (name="Key")
	def execute(self, context):
		bundles = objects_organise.get_bundles()
		if self.key in bundles:
			for obj in bundles[self.key]['objects']:
				obj.select_set(False)
		return {'FINISHED'}