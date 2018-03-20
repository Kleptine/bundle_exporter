import bpy
import os
import mathutils

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
	mode_package = bpy.props.EnumProperty(items= 
		[('name', 'Name', "Group by matching names"), 
		('space', 'Space', "Group by shared space"), 
		('group', 'Group', "Group by 'Groups'")], name = "Package Mode", default = 'name'
	)
	mode_origin = bpy.props.EnumProperty(items= 
		[('name_first', 'First', "Origin of first object sorted by name"), 
		('bottom_bounds', 'Bottom', "Bounds bottom center of group"), 
		('world_center', 'Scene', "The Scene center 0,0,0'")], name = "Origin From", default = 'name_first'
	)


def get_key(obj):
	return obj.name


def get_bundles():
	objects = []
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			objects.append(obj)

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

	# Sort alphabetically
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
		col.label(text="Bundle mode")
		row = col.row(align=True)
		row.prop(context.scene.FBXBundleSettings, "mode_package", text="Mode", expand=True)
		
		col = box.column(align=True)
		col.prop(context.scene.FBXBundleSettings, "mode_origin", text="Origin", expand=False)
		layout.separator()
		
		layout.label(text="Modify")
		box = layout.box()
		box.label(text="[] Copy Modifiers")
		box.label(text="[] Merge to single Mesh")

		# Get bundles
		bundles = get_bundles()


		row = layout.row()
		row.label('Files: '+str(len(bundles))+"x")
		
		if(len(bundles) > 0):
			row = layout.row()
			box = row.box()
			
			for fileName,objects in bundles.items():
				for i in range(0,len(objects)):
					row = box.row()
					if i ==0:
						label = text=fileName+".fbx";
						if len(objects) > 1:
							label+="   "+str(len(objects))+"x";
						row.label(label)
					else:
						row.label(text="")
						
					row.label(text=objects[i].name)







# registers
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.FBXBundleSettings = bpy.props.PointerProperty(type=FBXBundleSettings)
	bpy.utils.register_class(FBXBundleExporterPanel)


def unregister():
	bpy.utils.unregister_class(FBXBundleExporterPanel)
	del bpy.types.Scene.FBXBundleSettings


if __name__ == "__main__":
	register()
