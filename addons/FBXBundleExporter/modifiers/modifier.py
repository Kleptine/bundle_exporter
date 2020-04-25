import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

modifiers = []


class Settings(bpy.types.PropertyGroup):
	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)

class Modifier:
	label = "Modifier"
	id = 'modifier'
	url = ""

	def __init__(self):
		pass

	#region Description
	
	def settings_path(self):
		return "BGE_modifier_{}".format(self.id)


	def register(self):
		n = self.__module__.split(".")[-1]
		# print("Register base class: n:{} ".format(n))
		from bpy.utils import register_class
		exec("from . import {}".format(n))
		exec("register_class({}.Settings)".format(n))
		exec("bpy.types.Scene."+self.settings_path() + " = bpy.props.PointerProperty(type={}.Settings)".format(n))


	def unregister(self):
		n = self.__module__.split(".")[-1]
		from bpy.utils import unregister_class
		exec("from . import {}".format(n))
		exec("unregister_class({}.Settings)".format(n))
		exec("del "+"bpy.types.Scene."+self.settings_path() )


	def get(self, key):
		return eval("bpy.context.scene.{}.{}".format(self.settings_path(), key))
	

	def draw(self, layout):
		row = layout.row(align=True)
		row.prop( eval("bpy.context.scene."+self.settings_path()) , "active", text="")
		row.label(text="{}".format(self.label), icon='MODIFIER')

		r = row.row(align=True)
		r.enabled = self.get("active")
		r.alignment = 'RIGHT'
		from ..operators import BGE_OT_modifier_apply
		r.operator( BGE_OT_modifier_apply.bl_idname, icon='FILE_TICK' ).modifier_index = modifiers.index(self)

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
