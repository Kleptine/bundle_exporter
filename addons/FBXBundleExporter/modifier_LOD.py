import bpy, bmesh
import math
from . import modifier



class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	levels = bpy.props.IntProperty (
		default=2,
		min=1,
		max=5,
		subtype='FACTOR'
	)
	quality = bpy.props.FloatProperty (
		name="Merge Verts",
		default=0.3,
		min = 0.01,
		max = 1,
		description="Maximum quality ratio.",
		subtype='FACTOR'
	)


def get_quality(index, count, max_quality):
	return 1 - (index+1)/count * (1 - max_quality)


class Modifier(modifier.Modifier):
	label = "LOD"
	id = 'lod'


	def __init__(self):
		super().__init__()


	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			row = layout.row(align=True)
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "levels", text="Steps", icon='AUTOMERGE_ON')
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "quality", text="Quality", icon='AUTOMERGE_ON')

			col = layout.column(align=True)
			for i in range(0, self.get("levels")):
				r = col.row()
				r.enabled = False
				r.label(text="LOD{}".format(i+1))
				r = r.row()
				r.enabled = False
				r.alignment = 'RIGHT'
				r.label(text="{}%".format( math.ceil(get_quality(i, self.get("levels"), self.get("quality"))*100) ))
			# row_freeze = row.row()
			# row_freeze.enabled = self.get("merge_active")
			# row_freeze.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_distance")


	def process_objects(self, name, objects):
		# UNITY 	https://docs.unity3d.com/Manual/LevelOfDetail.html
		# UNREAL 	https://docs.unrealengine.com/en-us/Engine/Content/Types/StaticMeshes/HowTo/LODs
		# 			https://answers.unrealengine.com/questions/416995/how-to-import-lods-as-one-fbx-blender.html
		pass