import bpy, bmesh
from . import modifier


class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	source = bpy.props.StringProperty()



class Modifier(modifier.Modifier):
	label = "Copy Modifiers"
	mode = 'MODIFIERS'

	def __init__(self):
		super().__init__()


	def register(self):
		exec("bpy.types.Scene."+self.settings_path() + " = bpy.props.PointerProperty(type=Settings)")



	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			# Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects
			layout.prop_search(eval("bpy.context.scene."+self.settings_path()), "source",  bpy.context.scene, "objects")
			if self.get('source') in bpy.data.objects:
				count = len(bpy.data.objects[self.get('source')].modifiers)
				layout.label(text="copyies {}x modifiers".format(count))
