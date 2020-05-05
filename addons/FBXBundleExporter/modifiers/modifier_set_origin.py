import bpy, bmesh
import imp

from . import modifier

class BGE_mod_set_origin(modifier.BGE_mod_default):
	label = "Set Origin"
	id = 'set_origin'
	url = "http://renderhjs.net/fbxbundle/"
	type = 'MESH'
	icon = 'OBJECT_ORIGIN'

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)

	def draw(self, layout):
		super().draw(layout)
		if(self.active):
			# Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects
			
			row = layout.row(align=True)

	def process_objects(self, name, objects, helpers, armatures):
		pass