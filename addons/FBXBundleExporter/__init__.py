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
		
		col = layout.column(align=True)
		row = col.row(align=True)
		row.scale_y = 1.7
		row.operator(op_export.bl_idname, text="Export {}x".format(len(bundles)), icon='EXPORT')

		row = col.row(align=True)
		row.operator(op_fence.bl_idname, text="Fence", icon='STICKY_UVS_LOC')
		row.operator(op_fence_clear.bl_idname, text="Clear", icon='PANEL_CLOSE')
		
		layout.separator()

		
		if(len(bundles) > 0):

			for fileName,objects in bundles.items():

				# row = layout.row(align=True)
				box = layout.box()
				# box.scale_y = 0.8
				column = box.column(align=True)

				row = column.row(align=True)
				if(fileName == "unknown"):
					row.alert = True
				
				row.operator(op_select.bl_idname,text="{}x   {}.fbx".format(len(objects), fileName)).key = fileName
				r = row.row(align=True)
				r.alert = True
				r.operator(op_remove.bl_idname,text="", icon='X').key = fileName

				# col = row.column(align=True)
				# col.alignment = 'LEFT'
				# col.label(text="{}x".format(len(objects)))

				# col = box.column(align=True)
				for i in range(0,len(objects)):
					row = column.row(align=True)
					row.label(text=objects[i].name)



class op_select(bpy.types.Operator):
	bl_idname = "fbxbundle.select"
	bl_label = "Select"
	key = bpy.props.StringProperty (name="Key")
	def execute(self, context):
		bundles = get_bundles()
		if self.key in bundles:
			bpy.ops.object.select_all(action='DESELECT')
			for obj in bundles[self.key]:
				obj.select = True
		return {'FINISHED'}



class op_remove(bpy.types.Operator):
	bl_idname = "fbxbundle.remove"
	bl_label = "Remove"
	key = bpy.props.StringProperty (name="Key")
	def execute(self, context):
		bundles = get_bundles()
		if self.key in bundles:
			for obj in bundles[self.key]:
				obj.select = False
		return {'FINISHED'}



class op_fence(bpy.types.Operator):
	bl_idname = "fbxbundle.fence"
	bl_label = "Fence"

	def execute(self, context):
		print ("Fence Operator")
		return {'FINISHED'}



class op_fence_clear(bpy.types.Operator):
	bl_idname = "fbxbundle.fence_clear"
	bl_label = "Fence"

	def execute(self, context):
		print ("Fence clear Operator")
		return {'FINISHED'}



class op_export(bpy.types.Operator):
	bl_idname = "fbxbundle.export"
	bl_label = "Export"

	def execute(self, context):
		export_fbx( get_bundles() )
		return {'FINISHED'}



def export_fbx(bundles):
	print("_____________")

	if not os.path.dirname(bpy.data.filepath):
		raise Exception("Blend file is not saved")

	if bpy.context.scene.FBXBundleSettings.path == "":
		raise Exception("Export path not set")

	path_folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))

	for name,objects in bundles.items():
		path = os.path.join(path_folder, name)
		print("Export {}".format(path))
		# # offset
		# offset = objects[0].location.copy();
		
		# # Select Group
		# for object in objects:
		# 	object.select = True
		# 	object.location =  object.location.copy() - offset;#

		# #Export
		# path = os.path.join(dir, fileName)
		# export_FBX(path)

		# #Restore offset
		# for object in objects:
		# 	object.location=object.location + offset;



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
		# print("_________")

		# Do objects share same space with bounds?
		objects = get_objects()
		clusters = []

		for o in objects: 
			clusters.append({'bounds':ObjectBounds(o), 'objects':[o], 'merged':False})


		for clusterA in clusters:
			if len(clusterA['objects']) > 0:

				for clusterB in clusters:
					if clusterA != clusterB and len(clusterB['objects']) > 0:

						boundsA = clusterA['bounds']
						boundsB = clusterB['bounds']
						if boundsA.is_colliding(boundsB):
							
							# print("Merge {} --> {}x = {}".format(nA, len(clusterB['objects']), ",".join( [o.name for o in clusterB['objects'] ] )   ))
							for o in clusterB['objects']:
								clusterA['objects'].append( o )
							clusterB['objects'].clear()
							
							boundsA.combine(boundsB)

		for cluster in clusters:
			if obj in cluster['objects']:
				return cluster['objects'][0].name


	return "unknown"





def sort_objects_name(objects):
	names = {}
	for obj in objects:
		names[obj.name] = obj

	# now sort
	sorted_objects = []
	for key in sorted(names.keys()):
		sorted_objects.append(names[key])

	return sorted_objects








def get_objects():
	objects = []
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			objects.append(obj)

	return sort_objects_name(objects)



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



# registers
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.FBXBundleSettings = bpy.props.PointerProperty(type=FBXBundleSettings)


def unregister():
	bpy.utils.unregister_class(FBXBundleExporterPanel)
	del bpy.types.Scene.FBXBundleSettings


if __name__ == "__main__":
	register()
