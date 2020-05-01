import bpy, bmesh
import imp
import math
from mathutils import Vector

from . import modifier


class Settings(modifier.Settings):
	label = "Offset Transform"
	id = 'offset_transform'
	url = "http://renderhjs.net/fbxbundle/#modifier_offset"
	type = "MESH"

	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	source: bpy.props.StringProperty()

	def draw(self, layout):
		super().draw(layout)
		if(self.active):
			# Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects
			layout.prop_search(self, "source",  bpy.context.scene, "objects", text="Source")
			

			if self.source in bpy.data.objects:
				
				obj = bpy.data.objects[self.source]

				messages = []
				if obj.location.magnitude > 0:
					messages.append("Move x:{:.1f} y:{:.1f} z:{:.1f}".format(obj.location.x, obj.location.y, obj.location.z))
				
				if obj.rotation_euler.x != 0 or obj.rotation_euler.y != 0 or obj.rotation_euler.z != 0:
					rx,ry,rz = obj.rotation_euler.x * 180/math.pi, obj.rotation_euler.y * 180/math.pi, obj.rotation_euler.z * 180/math.pi
					messages.append("Rotate x:{:.0f}° y:{:.0f}° z:{:.0f}°".format(rx, ry, rz))

				if obj.scale.x != 1 or obj.scale.y != 1 or obj.scale.z != 1:
					messages.append("Scale x:{:.2f} y:{:.2f} z:{:.2f}".format(obj.scale.x, obj.scale.y, obj.scale.z))

				if len(messages) > 0:
					col = layout.column(align=True)
					for message in messages:
						row = col.row(align=True)
						row.enabled = False
						row.label(text= message)



	def process_objects(self, name, objects):
		if self.source in bpy.data.objects:
			source = bpy.data.objects[self.source]
			print("Offset... "+source.name)


			bpy.ops.object.mode_set(mode='OBJECT')

			prev_cursor_mode = bpy.context.space_data.pivot_point
			prev_cursor_location = bpy.context.scene.cursor.location

			# Export origin
			bpy.context.space_data.pivot_point = 'CURSOR'
			bpy.context.scene.cursor.location = Vector((0,0,0))

			for obj in objects:
				if obj != source:

					
					bpy.ops.object.select_all(action='DESELECT')
					bpy.context.view_layer.objects.active = obj
					obj.select_set(True)

					# Move
					bpy.ops.transform.translate(value=source.location, constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')

					# Rotate
					bpy.ops.transform.rotate(value=source.rotation_euler.x, axis=(1, 0, 0), proportional='DISABLED')
					bpy.ops.transform.rotate(value=source.rotation_euler.y, axis=(0, 1, 0), proportional='DISABLED')
					bpy.ops.transform.rotate(value=source.rotation_euler.z, axis=(0, 0, 1), proportional='DISABLED')
					
					# Scale
					bpy.ops.transform.resize(value=source.scale, constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')

			# Restore pivot & mode
			bpy.context.space_data.pivot_point = prev_cursor_mode
			bpy.context.scene.cursor.location = prev_cursor_location
		