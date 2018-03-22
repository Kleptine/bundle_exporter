import bpy
import os
import mathutils
from mathutils import Vector

from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)

bl_info = {
	"name": "FBX Bundle Exporter",
	"description": "Export object selection in FBX bundles",
	"author": "Hendrik Schoenmaker",
	"blender": (2, 7, 9),
	"version": (0, 1, 0),
	"category": "Import-Export",
	"location": "3D Viewport tools panel: FBX Bundle Exporter",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
}

class FBXBundleSettings(bpy.types.PropertyGroup):
	path = bpy.props.StringProperty (
		name="Output Path",
		default="",
		description="Define the path where to export",
		subtype='DIR_PATH'
	)
	mode_bundle = bpy.props.EnumProperty(items= 
		[('name', 'Name', "Group by matching names"), 
		('space', 'Space', "Group by shared space"), 
		('group', 'Group', "Group by 'Groups'")], name = "Bundle Mode", default = 'name'
	)
	mode_pivot = bpy.props.EnumProperty(items= 
		[('name_first', 'First Child', "First object sorted by name of the group"), 
		('bottom_bounds', 'Bottom Center', "Bottom center of the bounds of the group"), 
		('world_center', 'Scene Origin', "The Scene center 0,0,0'")], name = "Pivot From", default = 'name_first'
	)



class FBXBundleExporterPanel(bpy.types.Panel):
	bl_idname = "FBX_bundle_exporter_panel"
	bl_label = "FBX Bundle"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "FBX Bundle"
	bl_context = "objectmode"

	def draw(self, context):
		layout = self.layout
		
		box = layout.box()
		box.prop(context.scene.FBXBundleSettings, "path", text="")
		
		col = box.column(align=True)
		col.prop(context.scene.FBXBundleSettings, "mode_bundle", text="Bundle")
		col.prop(context.scene.FBXBundleSettings, "mode_pivot", text="Pivot", expand=False)
		# layout.separator()
		
		# layout.label(text="Add Modifier")
		# box = layout.box()
		# box.label(text="[] Copy Modifiers")
		# box.label(text="[] Merge to single Mesh")

		# Get bundles
		bundles = get_bundles()

		row = layout.row()
		row.label('Files: '+str(len(bundles))+"x")
		
		row = layout.row(align=True)
		row.operator(op_export.bl_idname, text="Export {}x".format(len(bundles)), icon='EXPORT')
		row.operator(op_fence.bl_idname, text="Fence", icon='STICKY_UVS_LOC')
		layout.separator()

		
		if(len(bundles) > 0):

			for fileName,objects in bundles.items():
				row = layout.row(align=True)
				box = row.box()

				row = box.row(align=True)
				if(fileName == "unknown"):
					row.alert = True
				row.operator(op_remove.bl_idname,text="", icon='X')
				row.operator(op_select.bl_idname,text=fileName+".fbx")#, icon='MATCUBE'

				col = row.column(align=True)
				col.alignment = 'LEFT'
				col.label(text="{}x".format(len(objects)))

				for i in range(0,len(objects)):
					row = box.row(align=True)
					row.label(text=objects[i].name)



class op_select(bpy.types.Operator):
	bl_idname = "fbxbundle.select"
	bl_label = "Select"

	def execute(self, context):
		print ("Select Operator")
		return {'FINISHED'}



class op_remove(bpy.types.Operator):
	bl_idname = "fbxbundle.remove"
	bl_label = "Remove"

	def execute(self, context):
		print ("Remove Operator")
		return {'FINISHED'}



class op_export(bpy.types.Operator):
	bl_idname = "fbxbundle.export"
	bl_label = "Export"

	def execute(self, context):
		print ("Export Operator")
		return {'FINISHED'}



class op_fence(bpy.types.Operator):
	bl_idname = "fbxbundle.fence"
	bl_label = "Fence"

	def execute(self, context):
		print ("Fence Operator")
		return {'FINISHED'}



def get_key(obj):
	mode = bpy.context.scene.FBXBundleSettings.mode_bundle
	if mode == 'name':
		name = obj.name
		# Remove blender naming digits, e.g. cube.001, cube.002,...
		if len(name)>= 4 and name[-4] == '.' and name[-3].isdigit() and name[-2].isdigit() and name[-1].isdigit():
			name = name[:-4]

		# Split
		split_chars = [' ','_','.','-']
		split = name.lower()
		for char in split_chars:
			split = split.replace(char,' ')
		
		# Combine
		strings = split.split(' ')
		if len(strings) > 1:
			name = '_'.join(strings[0:-1])
		else:
			name = strings[0]
		return name

	elif mode == 'group':
		if len(obj.users_group) >= 1:
			return obj.users_group[0].name

	elif mode == 'space':
		print("_________")

		# Do objects share same space with bounds?
		objects = get_objects()
		clusters = {}

		for obj_A in objects: 
			clusters[ObjectBounds(obj)] = [obj_A]
		
		removed = []

		for bounds_A in clusters:
			if bounds_A not in removed:
				for bounds_B in clusters:
					if bounds_B not in removed and bounds_A != bounds_B:

						if bounds_A.is_colliding(bounds_B):
							# Merge Objects
							for o in clusters[bounds_B]:
								if o not in clusters[bounds_A]:
									clusters[bounds_A].append(o)
							# Merge bounds
							bounds_A.combine(bounds_B)
							# Remove
							removed.append(bounds_B)
							# del clusters[bounds_B]
							continue
		for key in removed:
			del clusters[key]

		print("Clusters {}x".format(len(clusters)))






	return "unknown"

			# for obj_B in objects:
			# 	if obj_A != obj_B:

			# 		bounds = ObjectBounds(obj_B)

			# 		if bounds.is_colliding(bounds_B):


		# remaining = objects.copy()
		# for obj_A in objects:
		# 	if obj_A in remaining:
		# 		bounds = SceneBounds(obj_A)
		# 		remaining.remove(obj_A)
		# 		for obj_B in remaining:
		# 			print("Compare {} | {}".format(obj_A.name, obj_B.name))
		# 			bounds_B = SceneBounds(obj_B)
		# 			if bounds.is_colliding(bounds_B):
		# 				bounds.combine(bounds_B)
		# 				print("Combined ".format(obj_B.name))
		# 				remaining.remove(obj_B)
		# 				break
		
		
		# processed = []
		# groups = []
		# for i in range(0, len(objects)):
		# 	obj_A = objects[i]
			
		# 	if obj_A in processed:
		# 		continue

		# 	group = [obj_A]
		# 	processed.append(obj_A)
		# 	bounds = SceneBounds(obj_A)

		# 	if(i < len(objects)-1):
		# 		for j in range(i+1, len(objects)):
		# 			obj_B = objects[j]

		# 			if obj_B in processed:
		# 				continue

					
		# 			bounds_B = SceneBounds(obj_B)
		# 			if(is_colliding(bounds, bounds_B)):
		# 				print("Collide {} x {}".format(obj_A.name, obj_B.name))
		# 				group.append(obj_B)
		# 				processed.append(obj_B)
		# 				bounds.combine(bounds_B)

		# 	groups.append(group)

		# print("groups {}x".format(len(groups)))
		# if(len(groups) > 0):
		# 	for group in groups:
		# 		for obj_A in group:
		# 			if obj == obj_A:
		# 				return group[0].name
		
		# 	# print("Bounds {} | {} | {}".format(bounds.size, bounds.center, bounds.obj.name))
		# #take first object sorted by name
		# return obj.name
	



class ObjectBounds:
	obj = None
	bounds_min = Vector((0,0,0))
	bounds_max = Vector((0,0,0))
	size = Vector((0,0,0))
	center = Vector((0,0,0))

	def __init__(self, obj):
		self.obj = obj
		corners = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]

		self.bounds_min = Vector((corners[0].x, corners[0].y, corners[0].z))
		self.bounds_max = Vector((corners[0].x, corners[0].y, corners[0].z))
		for corner in corners:
			self.bounds_min.x = min(self.bounds_min.x, corner.x)
			self.bounds_min.y = min(self.bounds_min.y, corner.y)
			self.bounds_min.z = min(self.bounds_min.z, corner.z)
			self.bounds_max.x = max(self.bounds_max.x, corner.x)
			self.bounds_max.y = max(self.bounds_max.y, corner.y)
			self.bounds_max.z = max(self.bounds_max.z, corner.z)

		self.size = self.bounds_max - self.bounds_min
		self.center = self.bounds_min+(self.bounds_max-self.bounds_min)/2


	def combine(self, other):
		self.bounds_min = min(self.bounds_min, other.bounds_min)
		self.bounds_max = max(self.bounds_max, other.bounds_max)
		self.size = self.bounds_max - self.bounds_min
		self.center = self.bounds_min+(self.bounds_max-self.bounds_min)/2

	def is_colliding(self, other):
		def is_collide_1D(A_min, A_max, B_min, B_max):
			# One line is inside the other
			length_A = A_max-A_min
			length_B = B_max-B_min
			center_A = A_min + length_A/2
			center_B = B_min + length_B/2
			return abs(center_A - center_B) <= (length_A+length_B)/2

		collide_x = is_collide_1D(self.bounds_min.x, self.bounds_max.x, other.bounds_min.x, other.bounds_max.x)
		collide_y = is_collide_1D(self.bounds_min.y, self.bounds_max.y, other.bounds_min.y, other.bounds_max.y)
		collide_z = is_collide_1D(self.bounds_min.z, self.bounds_max.z, other.bounds_min.z, other.bounds_max.z)

		return collide_x and collide_y and collide_z



def get_objects():
	objects = []
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			objects.append(obj)

	return objects



def get_bundles():
	objects = get_objects()

	# Collect groups by key
	groups = []
	for obj in objects:
		key = get_key(obj)

		if(len(groups) == 0):
			groups.append([obj])
		else:
			isFound = False
			for group in groups:
				if key == get_key(group[0]):
					group.append(obj)
					isFound = True
					break
			if not isFound:
				groups.append([obj])

	# Sort keys alphabetically
	keys = [get_key(group[0]) for group in groups]
	keys.sort()
	key_groups = {}
	for key in keys:
		if key not in key_groups:
			key_groups[key] = []

		for group in groups:
			if key == get_key(group[0]):
				key_groups[key] = group
				break

	return key_groups






# registers
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.FBXBundleSettings = bpy.props.PointerProperty(type=FBXBundleSettings)


def unregister():
	bpy.utils.unregister_class(FBXBundleExporterPanel)
	del bpy.types.Scene.FBXBundleSettings


if __name__ == "__main__":
	register()
