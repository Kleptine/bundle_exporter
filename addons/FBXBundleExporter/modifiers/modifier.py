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

def create_local_settings(Settings, defaults_path, name):
	new_annotattions = {}
	
	for key in Settings.__annotations__:
		preferences_val = eval("{}.{}".format(defaults_path, key))
		prop_data = Settings.__annotations__[key][1]
		prop_data['default'] = preferences_val
		new_annotattions[key] = (Settings.__annotations__[key][0], prop_data)
		#new_annotattions[key]['default']=preferences_val
	SettingsScene = type(name+"Settings", (bpy.types.PropertyGroup,), {'__annotations__':new_annotattions})
	return SettingsScene

local_settings = []

def register_globals():
	for x in modifiers:
		x.register_global()

def register_locals():
	global local_settings
	local_settings = []
	for x in modifiers:
		x.register_local()

def unregister_globals():
	for i in reversed(range(0,len(modifiers))):
		x = modifiers[i]
		x.unregister_global()

def unregister_locals():
	from bpy.utils import unregister_class
	for i in reversed(range(0,len(local_settings))):
		x = local_settings[i]
		unregister_class(x)
	
	for i in reversed(range(0,len(modifiers))):
		x = modifiers[i]
		x.unregister_local()

class Modifier:
	label = "Modifier"
	id = 'modifier'
	url = ""

	def __init__(self, use_global_settings = False):
		self.use_global_settings = use_global_settings
		
	@classmethod
	def settings_name(cls):
		return "BGE_modifier_{}".format(cls.id)

	def settings_path_global(self):
		return "bpy.context.preferences.addons['{}'].preferences.BGE_modifier_{}".format(__name__.split('.')[0], self.id)
	
	def settings_path(self):
		if self.use_global_settings:
			return self.settings_path_global()
		return "bpy.context.scene.{}".format(self.settings_name())

	def register_global(self):
		n = self.__module__.split(".")[-1]
		# print("Register base class: n:{} ".format(n))
		from bpy.utils import register_class
		exec("from . import {}".format(n))
		exec("register_class({}.Settings)".format(n))

	def register_local(self):
		n = self.__module__.split(".")[-1]
		# print("Register base class: n:{} ".format(n))
		from bpy.utils import register_class
		exec("from . import {}".format(n))
		exec("local_settings.append(create_local_settings({}.Settings,\"{}\", \"{}\"))".format(n,self.settings_path_global(), self.id))
		exec("register_class(local_settings[-1])")
		exec("bpy.types.Scene."+self.settings_name() + " = bpy.props.PointerProperty(type=local_settings[-1])")

	def unregister_local(self):
		exec("del "+"bpy.types.Scene."+self.settings_name())
	
	def unregister_global(self):
		n = self.__module__.split(".")[-1]
		from bpy.utils import unregister_class
		exec("from . import {}".format(n))
		exec("unregister_class({}.Settings)".format(n))

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
