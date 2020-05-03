import bpy, bmesh
import imp

from . import modifier

from ..settings import prefix_copy
class BGE_mod_copy_modifiers(modifier.BGE_mod_default):
	label = "Copy Modifiers"
	id = 'copy_modifiers'
	url = "http://renderhjs.net/fbxbundle/#modifier_modifiers"
	type = 'MESH'
	icon = 'MODIFIER_DATA'

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	source: bpy.props.StringProperty()

	replace_references : bpy.props.BoolProperty(default=True)

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
				row.label(text="copies {}x modifiers".format(count))



	def process_objects(self, name, objects, helpers, armatures):
		source = self.get_object_from_name(self.source)

		if source:
			bpy.ops.object.select_all(action="DESELECT")

			for obj in objects:
				obj.select_set(True)

			source.select_set(True)
			bpy.context.view_layer.objects.active = source

			bpy.ops.object.make_links_data(type='MODIFIERS')

			if self.replace_references:
				for obj in objects:
					for mod in obj.modifiers:
						if hasattr(mod, 'object'):
							if mod.object.name.startswith(prefix_copy):
								if mod.object['__orig_name__'] in bpy.data.objects.keys():
									mod.object = bpy.data.objects[mod.object['__orig_name__']]

			source.select_set(False)
		else:
			print('MODIFIER_COPY_MODIFIERS source not found')

		return objects, helpers, armatures
		