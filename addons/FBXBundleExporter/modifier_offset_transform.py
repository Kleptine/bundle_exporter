import bpy, bmesh
import imp
import math

from . import modifier
imp.reload(modifier) 


class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	source = bpy.props.StringProperty()



class Modifier(modifier.Modifier):
	label = "Offset Transform"
	id = 'offset_transform'

	def __init__(self):
		super().__init__()


	def register(self):
		exec("bpy.types.Scene."+self.settings_path() + " = bpy.props.PointerProperty(type=Settings)")



	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			# Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects
			layout.prop_search(eval("bpy.context.scene."+self.settings_path()), "source",  bpy.context.scene, "objects", text="Source")
			if self.get('source') in bpy.data.objects:
				
				obj = bpy.data.objects[self.get('source')]

				messages = []
				if obj.location.magnitude > 0:
					messages.append("Move {:.0f},{:.0f},{:.0f}".format(obj.location.x, obj.location.y, obj.location.z))
				
				if obj.rotation_euler.x != 0 or obj.rotation_euler.y != 0 or obj.rotation_euler.z != 0:
					rx,ry,rz = obj.rotation_euler.x * 180/math.pi, obj.rotation_euler.y * 180/math.pi, obj.rotation_euler.z * 180/math.pi
					messages.append("Rotate {:.0f}°,{:.0f}°,{:.0f}°".format(rx, ry, rz))

				if obj.scale.x != 1 or obj.scale.y != 1 or obj.scale.z != 1:
					messages.append("Scale {:.1f},{:.1f},{:.1f}".format(obj.scale.x, obj.scale.y, obj.scale.z))

				if len(messages) > 0:
					col = layout.column(align=True)
					for message in messages:
						row = col.row(align=True)
						row.enabled = False
						row.label(text= message)



	def process_objects(self, name, objects):
		if self.get('source') in bpy.data.objects:
			source = bpy.data.objects[ self.get('source') ]
			print("Offset... "+source.name)
			for obj in objects:
				if obj != source:
					obj.location.x+= source.location.x
					obj.location.y+= source.location.y
					obj.location.z+= source.location.z

					obj.rotation_euler.x+= source.rotation_euler.x
					obj.rotation_euler.y+= source.rotation_euler.y
					obj.rotation_euler.z+= source.rotation_euler.z

					obj.scale.x*= source.scale.x
					obj.scale.y*= source.scale.y
					obj.scale.z*= source.scale.z

		