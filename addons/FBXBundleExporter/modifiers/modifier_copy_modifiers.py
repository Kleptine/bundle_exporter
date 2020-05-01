import bpy, bmesh
import imp

from . import modifier

class Settings(modifier.Settings):
	label = "Copy Modifiers"
	id = 'copy_modifiers'
	url = "http://renderhjs.net/fbxbundle/#modifier_modifiers"
	type = 'MESH'

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



	def process_objects(self, name, objects):
		if self.source in bpy.data.objects:
			source = bpy.data.objects[self.source]
			source.select_set(True)
			bpy.context.view_layer.objects.active = source

			bpy.ops.object.make_links_data(type='MODIFIERS')
			source.select_set(False)

		