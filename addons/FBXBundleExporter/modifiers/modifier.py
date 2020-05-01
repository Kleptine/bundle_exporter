import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

class Settings(bpy.types.PropertyGroup):
	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)

class Modifier:
	label = "Modifier"
	id = 'modifier'
	url = ""
	type = "MESH"

	def __init__(self, path = 'bpy.context.scene', use_global_settings = False):
		self.use_global_settings = use_global_settings
		self.path = path
		
	@classmethod
	def settings_name(cls):
		return "BGE_modifier_{}".format(cls.id)

	@classmethod
	def settings_path_global(cls):
		return "bpy.context.preferences.addons['{}'].preferences.BGE_modifier_{}".format(__name__.split('.')[0], cls.id)

	@classmethod
	def settings_path_local(cls):
		return "bpy.context.scene.{}".format(cls.settings_name())

	def settings_path_custom(self):
		return self.path
	
	def settings_path(self):
		if self.use_global_settings:
			return self.settings_path_global()
		return self.settings_path_local()

	def get(self, key):
		return eval("{}.{}".format(self.settings_path(), key))
	

	def draw(self, layout):
		row = layout.row(align=True)
		row.prop(eval(self.settings_path()), "active", text="")
		row.label(text="{}".format(self.label), icon='MODIFIER')

		r = row.row(align=True)
		r.enabled = self.get("active")
		r.alignment = 'RIGHT'
		if not self.use_global_settings:
			from ..operators import BGE_OT_modifier_apply
			r.operator( BGE_OT_modifier_apply.bl_idname, icon='FILE_TICK' ).modifier_id = self.id

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
