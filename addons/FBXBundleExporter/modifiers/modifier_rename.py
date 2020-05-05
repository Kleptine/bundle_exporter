import bpy, bmesh
import math
import imp
import os

from . import modifier

class BGE_mod_rename(modifier.BGE_mod_default):
	label = "Rename"
	id = 'rename'
	url = "http://renderhjs.net/fbxbundle/#modifier_rename"
	type = "GENERAL"
	icon = 'SYNTAX_OFF'
	priority = 999

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	path: bpy.props.StringProperty(default="{path}")
	file: bpy.props.StringProperty(default="{bundle}")
	obj: bpy.props.StringProperty(default="{object}")

	def draw(self, layout):
		super().draw(layout)
		if self.active:
			# row = layout.row(align=True)

			col = layout.column(align=True)
			col.prop( self , "path", text="Path")
			col.prop( self , "file", text="File")
			col.prop( self , "obj", text="Object")

	def remove_illegal_characters(self, value):
		# Fix wrong path seperators
		#chars = '\/'
		#for c in chars:
		#	value = value.replace(c,os.path.sep)

		# Remove illegal characters (windows, osx, linux)
		chars = '*?"<>|'
		for c in chars:
			value = value.replace(c,'')
		return value

	def format_object_name(self, bundle, name):
		val = self.obj
		val = val.replace("{object}", name)
		val = val.replace("{bundle}", bundle)
		val = val.replace("{scene}", bpy.context.scene.name)
		return self.remove_illegal_characters(val)



	def process_objects(self, name, objects, helpers, armatures):
		for obj in objects:
			obj.name = self.remove_illegal_characters( self.format_object_name(name, obj.name) )

		return objects, helpers, armatures



	def process_name(self, name):
		val = self.file
		val = val.replace("{bundle}", name)
		val = val.replace("{scene}", bpy.context.scene.name)
		return self.remove_illegal_characters( val )



	def process_path(self, name, path):
		val = self.path
		val = val.replace("{path}", path)
		val = val.replace("{bundle}", name)
		val = val.replace("{scene}", bpy.context.scene.name)
		return self.remove_illegal_characters( val )