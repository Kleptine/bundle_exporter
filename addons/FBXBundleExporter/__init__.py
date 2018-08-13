
if "bpy" in locals():
	import imp
	imp.reload(gp_draw)
	imp.reload(objects_organise)

	imp.reload(op_fence_clear)
	imp.reload(op_fence_draw)
	imp.reload(op_file_copy_unity_script)
	imp.reload(op_file_export)
	imp.reload(op_file_import)
	imp.reload(op_file_open_folder)
	imp.reload(op_pivot_ground)
	imp.reload(op_tool_geometry_fix)
	imp.reload(op_tool_pack_bundles)
	
	imp.reload(modifier) 
	imp.reload(modifier_collider) 
	imp.reload(modifier_LOD) 
	imp.reload(modifier_merge) 
	imp.reload(modifier_modifiers) 
	imp.reload(modifier_rename) 


else:
	from . import gp_draw
	from . import objects_organise

	from . import op_fence_clear
	from . import op_fence_draw
	from . import op_file_copy_unity_script
	from . import op_file_export
	from . import op_file_import
	from . import op_file_open_folder
	from . import op_pivot_ground
	from . import op_tool_geometry_fix
	from . import op_tool_pack_bundles

	from . import modifier
	from . import modifier_collider
	from . import modifier_LOD
	from . import modifier_merge
	from . import modifier_modifiers
	from . import modifier_rename

import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math
import bpy.utils.previews


bl_info = {
	"name": "FBX Bundle",
	"description": "Export object selections in FBX bundles",
	"author": "renderhjs",
	"blender": (2, 7, 9),
	"version": (1, 2, 0),
	"category": "3D View",
	"location": "3D View > Tools Panel > FBX Bundle",
	"warning": "",
	"wiki_url": "https://bitbucket.org/renderhjs/blender-addon-fbx-bundle",
	"tracker_url": "",
}

from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)


modifiers = list([
	modifier_merge.Modifier(),
	modifier_modifiers.Modifier(),
	modifier_LOD.Modifier(),
	modifier_collider.Modifier(),
	modifier_rename.Modifier()
	
])


class Panel_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	def draw(self, context):
		layout = self.layout


		box = layout.box()
		row = box.row()
		row.label(text="Unity Editor script")
		row.operator(op_file_copy_unity_script.op.bl_idname, icon='SAVE_COPY')
		col = box.column(align=True)
		col.label(text="Copies a Unity Editor script to automatically assign")
		col.label(text="existing materials by name matching names in Blender")
		



class FBXBundleSettings(bpy.types.PropertyGroup):
	path = bpy.props.StringProperty (
		name="Output Path",
		default="",
		description="Define the path where to export or import from",
		subtype='DIR_PATH'
	)
	padding = bpy.props.FloatProperty (
		name="Padding",
		default=0.15,
		min = 0,
		description="Padding for fences or space bundling",
		subtype='DISTANCE'
	)
	merge = bpy.props.BoolProperty (
		name="Merge",
		default=False,
		description="Merge objects in a bundle into a single mesh when exporting"
	)
	collapseBundles = bpy.props.BoolProperty (
		name="Collapse",
		default=False,
		description="Collapse Bundle list view"
	)


	copyModifier = bpy.props.BoolProperty (
		name="Merge",
		default=False,
		description="Merge objects in a bundle into a single mesh when exporting"
	)

	# LOD_enable = bpy.props.BoolProperty (
	# 	name="Merge",
	# 	default=False,
	# 	description=""
	# )
	# LOD_levels = bpy.props.IntProperty (
	# 	name="LOD Levels",
	# 	default=0,
	# 	min=0,
	# 	max=8,
	# 	description="LOD levels to generate"
	# )

	mode_bundle = bpy.props.EnumProperty(items= 
		[('NAME', 'Name', "Bundle by matching object names"), 
		('PARENT', 'Parent', "Bundle by the parent object"), 
		# ('SPACE', 'Space', "Bundle by shared space"), 
		('GROUP', 'Group', "Bundle by 'Groups'"),
		('MATERIAL', 'Material', "Bundle by matching material names"),
		('SCENE', 'Scene', "Bundle by current scene")
		], name = "Bundle Mode", default = 'NAME'
	)
	mode_pivot = bpy.props.EnumProperty(items=[
		('OBJECT_FIRST', 'First Name', "Pivot at the first object sorted by name"), 
		('OBJECT_LOWEST', 'Lowest Object', "Pivot at the lowest Z object's pivot"),
		('BOUNDS_BOTTOM', 'Bottom Center', "Pivot at the bottom center of the bounds of the bundle"), 
		('SCENE', 'Scene 0,0,0', "Pivot at the Scene center 0,0,0'"),
		('PARENT', 'Parent', "Pivot from the parent object")
		], name = "Pivot From", default = 'OBJECT_FIRST'
	)
	target_platform = bpy.props.EnumProperty(items= 
		[	
			('UNITY', 'Unity ', 'Unity engine export, objects are rotated -90° x axis'),
			('UNREAL', 'Unreal ', 'Unreal engine export'),
			('BLENDER', 'Blender', 'Default Blender export'),
			('GLTF', 'glTF', 'GL Transmission Format')
		], 
		description="Target platform for the FBX exports.",
		name = "Target Platform", 
		default = 'UNITY'
	)


class Mode:
	extension = 'fbx'

	def __init__(self, extension):
		self.extension = extension


modes = {
	'UNITY' : Mode( extension='fbx'),
	'UNREAL' : Mode( extension='fbx'),
	'BLENDER' : Mode( extension='fbx'),
	'GLTF' : Mode( extension='gltf')
}



class Panel_Core(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_core"
	bl_label = " "
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "FBX Bundle"
	bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout
		box = layout.box()

		row = box.row()
		row.label(text='Settings', icon='PREFERENCES')

		icon = icon_get(bpy.context.scene.FBXBundleSettings.target_platform.lower())
		row.prop(bpy.context.scene.FBXBundleSettings, "target_platform", text="", icon_value=icon)
		


		if bpy.app.debug_value != 0:
			row = box.row(align=True)
			row.alert = True
			row.operator(op_debug_setup.bl_idname, text="Setup", icon='COLOR')
			row.operator(op_debug_lines.bl_idname, text="Draw", icon='GREASEPENCIL')


		col = box.column(align=True)

		row = col.row(align=True)
		if context.scene.FBXBundleSettings.path == "":
			row.alert = True
		row.prop(context.scene.FBXBundleSettings, "path", text="")
		row.operator(op_file_open_folder.op.bl_idname, text="", icon='FILE_FOLDER')


		row = col.row(align=True)
		row.prop(context.scene.FBXBundleSettings, "mode_bundle", text="", icon='GROUP')
		row.prop(context.scene.FBXBundleSettings, "mode_pivot", text="", icon='OUTLINER_DATA_EMPTY', expand=False)
		

		col.prop(context.scene.FBXBundleSettings, "padding", text="Padding", expand=True)
		col.prop(context.scene.FBXBundleSettings, "merge", text="Merge Meshes", expand=True)

		# Warnings
		if context.scene.FBXBundleSettings.path == "":
			box = col.box()
			box.label(text="No path defined", icon='ERROR')

		elif bpy.context.scene.unit_settings.scale_length != 1.00:
			box = col.box()
			box.label(text="Scene units not in meters", icon='ERROR')

		


class Panel_Tools(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_tools"
	bl_label = "Tools"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "FBX Bundle"
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()

		


		
		# Get bundles
		bundles = objects_organise.get_bundles()


		# col = layout.column(align=True)

		# col.separator()

		row = col.row(align=True)
		row.operator(op_fence_draw.op.bl_idname, text="Draw Fences", icon='GREASEPENCIL')
		row.operator(op_fence_clear.op.bl_idname, text="", icon='PANEL_CLOSE')

		col.separator()

		row = col.row(align=True)
		row.operator(op_pivot_ground.op.bl_idname, text="Ground Pivot", icon='OUTLINER_DATA_EMPTY')

		col.separator()

		col.operator(op_tool_geometry_fix.op.bl_idname, text="Fix Geometry", icon='MESH_ICOSPHERE')
		
		col.separator()

		col.operator(op_tool_pack_bundles.op.bl_idname, text="Pack Bundles", icon='UGLYPACKAGE')
		



		if bpy.app.debug_value != 0:
			row = layout.row(align=True)
			row.alert =True
			row.operator(op_fence_clear.op.bl_idname, text="Pack", icon='IMGDISPLAY')
			row.operator(op_fence_clear.op.bl_idname, text="Align Z", icon='TRIA_DOWN_BAR')
			layout.separator()




'''
class Panel_Modifiers(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_modifiers"
	bl_label = "Modifiers"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "FBX Bundle"
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()


		global modifiers
		mods = modifiers

		col.label(text="Modifiers {}x".format(len(modifiers)))	
		for modifier in mods:
			box = col.box()
			modifier.draw(box)
			
		# 


		# col.prop(context.scene.FBXBundleSettings, "LOD_enable", text="LOD", expand=True)
'''



class Panel_Files(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_files"
	bl_label = "Bundles"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "FBX Bundle"
	bl_context = "objectmode"
	# bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()

		# Get bundles
		bundles = objects_organise.get_bundles()

		icon = icon_get(bpy.context.scene.FBXBundleSettings.target_platform.lower())

		col = layout.column(align=True)	


		

		row = col.row(align=True)
		row.operator(op_file_import.op.bl_idname, text="Import", icon='IMPORT')
		row = col.row(align=True)
		row.scale_y = 1.85
		row.operator(op_file_export.op.bl_idname, text="Export {}x".format(len(bundles)), icon_value=icon)
		
		layout.separator()

		col.prop(context.scene.FBXBundleSettings, "collapseBundles", text="Collapse View", expand=True)

		mode = bpy.context.scene.FBXBundleSettings.target_platform
		
		# merge = 
		if(len(bundles) > 0):
			# box_files = layout.box()
			# box_files.active = False
			if len(bundles) == 1:
				layout.label(text = "1x Bundle")
			else:
				layout.label(text = "{}x Bundles".format(len(bundles)))


			# Display bundles
			for fileName,objects in bundles.items():

				# row = layout.row(align=True)
				box = layout.box()
				# box.scale_y = 0.8
				column = box.column(align=True)

				row = column.row(align=True)
				if(fileName == "unknown"):
					row.alert = True
				
				# Icon type
				icon = 'MESH_CUBE';
				if objects_organise.get_objects_animation(objects):
					icon = 'RENDER_ANIMATION';

				# Show label for FBX bundle
				label = "{}.fbx".format(fileName);
				if(len(objects) > 1):
					label = "{}.{}  {}x".format(fileName, modes[mode].extension, len(objects));

				row.operator(op_select.bl_idname,icon=icon, emboss=False, text=label).key = fileName
				r = row.row(align=True)
				r.alert = True
				r.operator(op_remove.bl_idname,text="", icon='X').key = fileName

				# col = row.column(align=True)
				# col.alignment = 'LEFT'
				# col.label(text="{}x".format(len(objects)))

				# col = box.column(align=True)
				if not context.scene.FBXBundleSettings.collapseBundles:
					for i in range(0,len(objects)):
						row = column.row(align=True)
						row.active = not bpy.context.scene.FBXBundleSettings.merge
						row.label(text=objects[i].name)






class op_debug_lines(bpy.types.Operator):
	bl_idname = "fbxbundle.debug_lines"
	bl_label = "Debug"

	def execute(self, context):
		print ("Debug Operator")

		gp_draw.draw_debug()

		return {'FINISHED'}


class op_debug_setup(bpy.types.Operator):
	bl_idname = "fbxbundle.debug_setup"
	bl_label = "Setup"

	def execute(self, context):
		print ("Debug Setup Operator")

		# Disable grid
		bpy.context.space_data.show_axis_x = False
		bpy.context.space_data.show_axis_y = False
		bpy.context.space_data.show_axis_z = False
		bpy.context.space_data.grid_lines = 6
		bpy.context.space_data.grid_subdivisions = 1
		bpy.context.space_data.grid_scale = 1
		bpy.context.space_data.show_floor = False

		bpy.context.space_data.show_all_objects_origin = True


		return {'FINISHED'}


class op_select(bpy.types.Operator):
	bl_idname = "fbxbundle.select"
	bl_label = "Select"
	key = bpy.props.StringProperty (name="Key")
	def execute(self, context):
		bundles = objects_organise.get_bundles()
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
		bundles = objects_organise.get_bundles()
		if self.key in bundles:
			for obj in bundles[self.key]:
				obj.select = False
		return {'FINISHED'}




def icon_get(name):
	if name not in preview_icons:
		print("Icon '{}' not found ".format(name))
	return preview_icons[name].icon_id


preview_icons = None
def icon_register(fileName):
	name = fileName.split('.')[0]   # Don't include file extension
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	preview_icons.load(name, os.path.join(icons_dir, fileName), 'IMAGE')

def icons_unregister():
	global preview_icons
	bpy.utils.previews.remove(preview_icons)
	preview_icons = None
	

# registers
def register():
	bpy.utils.register_module(__name__)

	# Register scene settings
	bpy.types.Scene.FBXBundleSettings = bpy.props.PointerProperty(type=FBXBundleSettings)

	# Register Icons
	global preview_icons
	preview_icons = bpy.utils.previews.new()

	icons = [
		"unity.png", 
		"unreal.png", 
		"blender.png",
		"gltf.png"
	]
	for icon in icons:
		icon_register(icon)


def unregister():
	bpy.utils.unregister_module(__name__)

	#Unregister Settings
	del bpy.types.Scene.FBXBundleSettings

	# Remove icons
	icons_unregister()


if __name__ == "__main__":
	register()

