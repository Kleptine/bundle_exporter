import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

class Settings(bpy.types.PropertyGroup):
	label = "Modifier"
	id = 'modifier'
	url = ""
	type = "MESH"
	global_settings = True

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)
		
	@classmethod
	def settings_name(cls):
		return "BGE_modifier_{}".format(cls.id)
	
	@classmethod
	def settings_path_global(cls):
		return "bpy.context.preferences.addons['{}'].preferences.modifier_preferences.BGE_modifier_{}".format(__name__.split('.')[0], cls.id)


	def draw(self, layout):
		row = layout.row(align=True)
		row.prop(self, "active", text="")
		row.label(text="{}".format(self.label), icon='MODIFIER')

		r = row.row(align=True)
		r.enabled = self.active
		r.alignment = 'RIGHT'
		#r.operator( BGE_OT_modifier_apply.bl_idname, icon='FILE_TICK' ).modifier_id = self.id

		r = row.row(align=True)
		r.alignment = 'RIGHT'
		r.operator("wm.url_open", text="", icon='QUESTION').url = self.url
		
	def print(self):
		pass
		# print("Modifier '{}'' mode: {}".format(label, mode))


	def process_objects(self, name, objects):
		return objects


	def process_name(self, name):
		return name


	def process_path(self, name, path):
		return path
