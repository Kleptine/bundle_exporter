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
	id = 'modifier'

	def __init__(self):
		print("Create class modifier")
		pass

	#region Description
	
	def settings_path(self):
		return "FBXBundle_modifier_{}".format(self.id)


	def register(self):
		exec("bpy.types.Scene."+self.settings_path() + " = bpy.props.PointerProperty(type=Settings)")


	def unregister(self):
		exec("del "+"bpy.types.Scene."+self.settings_path() )


	def get(self, key):
		return eval("bpy.context.scene.{}.{}".format(self.settings_path(), key))
	

	def draw(self, layout):
		# row.prop(bpy.context.scene.FBXBundleSettings, "target_platform", text="", icon_value=icon)
		
		# print("Set: {}".format(self.settings))
		# exec("layout.prop( "+self.settings_path()+", 'active', text='Active')" )

		row = layout.row(align=True)
		row.prop( eval("bpy.context.scene."+self.settings_path()) , "active", text="")
		row.label(text="{}".format(self.label), icon='MODIFIER')

		if(self.get("active")):
			layout.label(text="ACTIVE !!!!", icon='MODIFIER')
		
		# layout.prop( bpy.types.Scene.FBXBundle_modifier_merge , "active", text="Active")
		# layout.prop( exec("context.scene."+self.settings_path()) , "active", text="Active")


		# layout.prop( exec( self.settings_path() ) , "active", text="Active")




		


	def print(self):
		print("Modifier '{}'' mode: {}".format(label, mode))


	def process_export(fileName, objects):
		pass


	def process_filename(fileName):
		return fileName
