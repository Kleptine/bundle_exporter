import bpy, bmesh
import imp

from . import modifier

class BGE_mod_custom_pivot(modifier.BGE_mod_default):
	label = "Custom Pivot"
	id = 'custom_pivot'
	url = "http://renderhjs.net/fbxbundle/"
	type = 'MESH'
	icon = 'EMPTY_ARROWS'

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

			if self.source in bpy.data.objects:
				row = layout.row()
				row.enabled = False

				row.separator()
				count = len(bpy.data.objects[self.source].modifiers)
				row.label(text="copyies {}x modifiers".format(count))



	def process_pivot(self, pivot, meshes, helpers, armatures):
		if self.source in bpy.data.objects:
			source = bpy.data.objects[self.source]

			return bpy.data.objects[self.source].location
		return pivot

		