import bpy, bmesh
import math
import imp

from . import modifier



class Settings(modifier.Settings):
	label = "Vertex AO"
	id = 'vertex_ao'
	url = "http://renderhjs.net/fbxbundle/#modifier_ao"
	type = "MESH"

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	contrast: bpy.props.FloatProperty (
		default=0.5,
		min = 0,
		max = 1,
		description="Contrast ratio, 0 is identical to plain 'dirty colors'",
		subtype='FACTOR'
	)

	def draw(self, layout):
		super().draw(layout)
		if self.active:
			col = layout.column(align=True)

			row = col.row(align=True)
			row.separator()
			row.separator()
			row.prop( self , "contrast", text="Contrast")

	def process_objects(self, name, objects):
		

		contrast = self.contrast

		for obj in objects:
			bpy.ops.object.select_all(action="DESELECT")
			obj.select_set(True)
			bpy.context.view_layer.objects.active = obj

			# Set AO vertex colors
			bpy.ops.object.mode_set(mode='VERTEX_PAINT')
			
			bpy.context.tool_settings.vertex_paint.brush.color = (1, 1, 1)
			bpy.ops.paint.vertex_color_set()
			bpy.ops.paint.vertex_color_dirt(blur_strength=1, blur_iterations=1, clean_angle= math.pi - (1-contrast) * math.pi/2 , dirt_angle=contrast * math.pi/2)

			# Back to object mode
			bpy.ops.object.mode_set(mode='OBJECT')

		return objects