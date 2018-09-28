import bpy, bmesh
import math
import imp
import os
from . import objects_organise
from . import modifier
imp.reload(modifier) 




class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	path = bpy.props.StringProperty(default="{path}")
	file = bpy.props.StringProperty(default="{bundle}")
	obj = bpy.props.StringProperty(default="{object}")




class Modifier(modifier.Modifier):
	label = "Rename"
	id = 'rename'


	def __init__(self):
		super().__init__()


	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			# row = layout.row(align=True)

			col = layout.column(align=True)
			col.prop( eval("bpy.context.scene."+self.settings_path()) , "path", text="Path")
			col.prop( eval("bpy.context.scene."+self.settings_path()) , "file", text="File")
			col.prop( eval("bpy.context.scene."+self.settings_path()) , "obj", text="Object")


			bundles = objects_organise.get_bundles()
			col = layout.column(align=True)
			col.enabled = False

			max_obj = 2
			max_file = 2

			path = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))
			for name,objects in bundles.items():
				full = self.process_path("name", path)+" / "+self.process_name(name) +" .ext"
				

				col.label(text= full )
				for obj in objects:
					row = col.row(align=True)
					row.separator()
					row.separator()
					row.label(text= self.format_object_name(name, obj.name) )
					break




	def format_object_name(self, bundle, name):
		val = self.get("obj")
		val = val.replace("{object}", name)
		val = val.replace("{bundle}", bundle)
		val = val.replace("{scene}", bpy.context.scene.name)
		return val



	def process_objects(self, name, objects):
		for obj in objects:
			obj.name = self.format_object_name(name, obj.name)

		return objects



	def process_name(self, name):
		val = self.get("file")
		val = val.replace("{bundle}", name)
		val = val.replace("{scene}", bpy.context.scene.name)
		return val


	def process_path(self, name, path):
		val = self.get("path")
		val = val.replace("{path}", path)
		val = val.replace("{bundle}", name)
		val = val.replace("{scene}", bpy.context.scene.name)
		return val