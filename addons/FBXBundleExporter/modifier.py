import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

import imp

from . import op_modifier_apply
imp.reload(op_modifier_apply)

from . import modifiers
imp.reload(modifiers)


class Settings(bpy.types.PropertyGroup):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)


class Modifier:
	mode = 'NONE'
	label = "Modifier"
	id = 'modifier'

	def __init__(self):
		print("Create class modifier")
		pass

	#region Description
	
	def settings_path(self):
		return "FBXBundle_modifier_{}".format(self.id)


	def register(self):
		n = self.__module__.split(".")[-1]
		# print("Register base class: n:{} ".format(n))

		exec("from . import {}".format(n))
		exec("bpy.types.Scene."+self.settings_path() + " = bpy.props.PointerProperty(type={}.Settings)".format(n))


	def unregister(self):
		exec("del "+"bpy.types.Scene."+self.settings_path() )


	def get(self, key):
		return eval("bpy.context.scene.{}.{}".format(self.settings_path(), key))
	

	def draw(self, layout):
		row = layout.row(align=True)
		row.prop( eval("bpy.context.scene."+self.settings_path()) , "active", text="")
		row.label(text="{}".format(self.label), icon='MODIFIER')

		r = row.row()
		r.enabled = self.get("active")
		r.alignment = 'RIGHT'
		r.operator( op_modifier_apply.op.bl_idname, icon='FILE_TICK' ).modifier_index = modifiers.modifiers.index(self)


	def print(self):
		print("Modifier '{}'' mode: {}".format(label, mode))


	def process_objects(self, name, objects):
		return objects


	def process_name(self, name):
		return name
