import bpy

from .. import objects_organise
from .. import bundle

class BGE_OT_select(bpy.types.Operator):
	bl_idname = "bge.select"
	bl_label = "Select"

	index: bpy.props.IntProperty (name="index")
	def execute(self, context):
		bpy.context.scene.BGE_Settings.bundles[self.index].select()
		return {'FINISHED'}

class BGE_OT_create_bundle(bpy.types.Operator):
	bl_idname = "bge.create_bundle"
	bl_label = "Create Bundle"

	def execute(self, context):
		#bundles = objects_organise.get_bundles()
		bundle.create_bundles_from_selection()
		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return len(bpy.context.selected_objects) > 0


class BGE_OT_remove(bpy.types.Operator):
	bl_idname = "bge.remove"
	bl_label = "Remove"

	index: bpy.props.IntProperty (name="index")
	def execute(self, context):
		bpy.context.scene.BGE_Settings.bundles.remove(self.index)
		return {'FINISHED'}