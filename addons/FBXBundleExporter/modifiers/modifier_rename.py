import bpy, bmesh
import math
import imp
import os
from .. import objects_organise

from . import modifier
from .. import platforms


class BGE_mod_rename(modifier.BGE_mod_default):
	label = "Rename"
	id = 'rename'
	url = "http://renderhjs.net/fbxbundle/#modifier_rename"
	type = "GENERAL"

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


			bundles = objects_organise.get_bundles()
			mode = bpy.context.scene.BGE_Settings.target_platform

			if mode in platforms.platforms:
				# label = 
				col = layout.column(align=True)
				col.enabled = False

				path = os.path.dirname( bpy.path.abspath( bpy.context.scene.BGE_Settings.path ))
				for name,data in bundles.items():
					objects = data['objects']
					full = self.process_path(name, path)+"{}".format(os.path.sep)+platforms.platforms[mode].get_filename( self.process_name(name) )  
					

					col.label(text= full )
					for obj in objects:
						row = col.row(align=True)
						row.separator()
						row.separator()
						row.label(text= self.format_object_name(name, obj.name) )
						break
					break



	def remove_illegal_characters(self, value):
		# Fix wrong path seperators
		chars = '\/'
		for c in chars:
			value = value.replace(c,os.path.sep)

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



	def process_objects(self, name, objects):
		for obj in objects:
			obj.name = self.remove_illegal_characters( self.format_object_name(name, obj.name) )

		return objects



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