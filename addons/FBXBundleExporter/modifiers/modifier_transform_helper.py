import bpy, bmesh
import imp

from . import modifier

class BGE_mod_transform_helpers(modifier.BGE_mod_default):
	label = "Transfrom Helpers"
	id = 'transform_helpers'
	url = "http://renderhjs.net/fbxbundle/"
	type = 'HELPER'
	icon = 'EMPTY_ARROWS'

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	scale: bpy.props.FloatVectorProperty(default = (0.01,0.01,0.01),subtype = 'XYZ',size=3)

	def draw(self, layout):
		super().draw(layout)
		if(self.active):
			# Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects
			
			row = layout.row(align=True)
			row.separator()
			row.separator()

			row.prop(self, "scale", text="Scale")


	def process_objects(self, name, objects, helpers, armatures):
		for x in helpers:
			x.scale *= self.scale 

		return objects, helpers, armatures