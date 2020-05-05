import bpy, bmesh
import imp

from . import modifier

class BGE_mod_custom_pivot(modifier.BGE_mod_default):
	label = "Custom Pivot"
	id = 'custom_pivot'
	url = "http://renderhjs.net/fbxbundle/"
	type = 'MESH'
	icon = 'EMPTY_ARROWS'
	priority = 10

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	source: bpy.props.StringProperty()

	def draw(self, layout):
		super().draw(layout)
		if(self.active):
			# Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects
			
			row = layout.row(align=True)
			row.separator()
			row.separator()

			row.prop_search(self, "source",  bpy.context.scene, "objects", text="Source")


	def process_pivot(self, pivot, meshes, helpers, armatures):
		source = self.get_object_from_name(self.source)
		if source:
			return source.location
		return pivot

		