import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

class Settings(bpy.types.PropertyGroup):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)


class Modifier:
	mode = 'NONE'
	label = "Modifier"
	settings_id = 'modifier'

	def __init__(self):
		print("Create class modifier")
		pass


	def settings_path(self):
		return "FBXBundle_modifier_{}".format(self.settings_id)


	def register(self):
		# bpy.utils.register_class(Settings)
		# exec("bpy.utils.register_class(Settings)")
		exec("bpy.types.Scene."+self.settings_path() + " = bpy.props.PointerProperty(type=Settings)")


	def unregister(self):
		exec("del "+"bpy.types.Scene."+self.settings_path() )
		# bpy.types.Scene.FBXBundle_modifier_merge = bpy.props.PointerProperty(type=Settings)
	

	
	def draw(self, layout):
		# row.prop(bpy.context.scene.FBXBundleSettings, "target_platform", text="", icon_value=icon)
		
		# print("Set: {}".format(self.settings))
		# exec("layout.prop( "+self.settings_path()+", 'active', text='Active')" )


		layout.prop( eval("bpy.context.scene."+self.settings_path()) , "active", text="Active")


		# layout.prop( bpy.types.Scene.FBXBundle_modifier_merge , "active", text="Active")
		# layout.prop( exec("context.scene."+self.settings_path()) , "active", text="Active")


		# layout.prop( exec( self.settings_path() ) , "active", text="Active")




		layout.label(text="{}".format(self.label), icon='MODIFIER')


	def print(self):
		print("Modifier '{}'' mode: {}".format(label, mode))


	def process_export(fileName, objects):
		pass


	def process_filename(fileName):
		return fileName
