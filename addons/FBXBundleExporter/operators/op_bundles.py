import bpy

from .. import objects_organise
from .. import bundles
from .. import modifiers

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
		bundles.create_bundles_from_selection()
		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return len(bpy.context.selected_objects) > 0


mesh_modifiers = [(x['global'].id, x['global'].label, "add " + x['global'].label, x['global'].icon, x['global'].unique_num) for x in modifiers.modifiers_dict.values() if x['global'].type == 'MESH']
general_modifiers = [(x['global'].id, x['global'].label, "add " + x['global'].label, x['global'].icon, x['global'].unique_num) for x in modifiers.modifiers_dict.values() if x['global'].type == 'GENERAL']
helper_modifiers = [(x['global'].id, x['global'].label, "add " + x['global'].label, x['global'].icon, x['global'].unique_num) for x in modifiers.modifiers_dict.values() if x['global'].type == 'HELPER']
armature_modifiers = [(x['global'].id, x['global'].label, "add " + x['global'].label, x['global'].icon, x['global'].unique_num) for x in modifiers.modifiers_dict.values() if x['global'].type == 'ARMATURE']

modifier_enum = [("", "General", "description", "MODIFIER", 0)] + general_modifiers + [("", "Mesh", "description", "OUTLINER_OB_MESH", 0)] + mesh_modifiers + [("", "Helper", "description", "OUTLINER_OB_EMPTY", 0)] + helper_modifiers + [("", "Armature", "description", "OUTLINER_OB_ARMATURE", 0)] + armature_modifiers
class BGE_OT_override_bundle_modifier(bpy.types.Operator):
	bl_idname = "bge.override_bundle_modifier"
	bl_label = "Add Override Modifier"

	option : bpy.props.EnumProperty(items= modifier_enum)

	#collection: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)

	def execute(self, context):
		#bundles = objects_organise.get_bundles()
		print(self.option)
		mods = modifiers.get_modifiers(bpy.context.scene.BGE_Settings.bundles[bpy.context.scene.BGE_Settings.bundle_index].override_modifiers)
		for x in mods:
			if x.id == self.option:
				x.active=True
		return {'FINISHED'}

class BGE_OT_add_bundle_modifier(bpy.types.Operator):
	bl_idname = "bge.add_bundle_modifier"
	bl_label = "Add Export Modifier"

	option : bpy.props.EnumProperty(items= modifier_enum)

	#collection: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)

	def execute(self, context):
		#bundles = objects_organise.get_bundles()
		print(self.option)
		mods = modifiers.get_modifiers(bpy.context.scene.BGE_Settings.scene_modifiers)
		for x in mods:
			if x.id == self.option:
				x.active=True
		return {'FINISHED'}

class BGE_OT_remove(bpy.types.Operator):
	bl_idname = "bge.remove"
	bl_label = "Remove"

	index: bpy.props.IntProperty (name="index")
	def execute(self, context):
		bpy.context.scene.BGE_Settings.bundles.remove(self.index)
		return {'FINISHED'}