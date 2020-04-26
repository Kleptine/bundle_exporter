from . import gp_draw
from . import objects_organise

from . import modifiers
from . import platforms
from . import operators

from . import icons

import bpy, bmesh
import os
import math
import bpy.utils.previews

from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)

from .__init__ import mode_bundle_types, mode_pivot_types, target_platform_types


def set_path(self, value):
	#checks if the provided path is inside a subdirectory of the current file to save it as a relative path
	if bpy.data.is_saved:
		value = os.path.realpath(bpy.path.abspath(value))
		file_path = os.path.dirname(os.path.realpath(bpy.path.abspath(bpy.data.filepath)))
		if os.path.commonprefix([os.path.realpath(bpy.path.abspath(value)), file_path]) == file_path:
			value = bpy.path.relpath(value)

	self.real_path = value

def get_path(self):
	return self.real_path

class BGE_Settings(bpy.types.PropertyGroup):
	real_path: bpy.props.StringProperty ()
	path: bpy.props.StringProperty (
		name="Output Path",
		default="",
		description="Define the path where to export or import from",
		subtype='DIR_PATH',
		get=get_path,
		set=set_path
	)
	padding: bpy.props.FloatProperty (
		name="Padding",
		default=0.15,
		min = 0,
		description="Padding for fences or space bundling",
		subtype='DISTANCE'
	)
	collapseBundles: bpy.props.BoolProperty (
		name="Collapse",
		default=False,
		description="Compact list view"
	)
	include_children: bpy.props.BoolProperty (
		name="Incl. Children",
		default=False,
		description="Include nested children in bundles, e.g parent or group."
	)
	recent: bpy.props.StringProperty (
		name="Recent export",
		default=""
	)

	mode_bundle: bpy.props.EnumProperty(items= mode_bundle_types, name = "Bundle Mode", default = bpy.context.preferences.addons[__name__.split('.')[0]].preferences.mode_bundle)
	mode_pivot: bpy.props.EnumProperty(items=mode_pivot_types, name = "Pivot From", default = bpy.context.preferences.addons[__name__.split('.')[0]].preferences.mode_pivot)
	target_platform: bpy.props.EnumProperty(items= target_platform_types, description="Target platform for the FBX exports.",name = "Target Platform", default = bpy.context.preferences.addons[__name__.split('.')[0]].preferences.target_platform)



class BGE_PT_core_panel(bpy.types.Panel):
	bl_idname = "BGE_PT_core_panel"
	bl_label = " "
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Game Exporter"
	bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout
		box = layout.box()

		row = box.row(align=True)
		row.label(text='Settings', icon='PREFERENCES')

		icon = icons.icon_get(bpy.context.scene.BGE_Settings.target_platform.lower())
		row.prop(bpy.context.scene.BGE_Settings, "target_platform", text="", icon_value=icon)
		row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_platform"


		mode = bpy.context.scene.BGE_Settings.target_platform

		if bpy.app.debug_value != 0:
			row = box.row(align=True)
			row.alert = True
			row.operator(operators.BGE_PT_debug_setup.bl_idname, text="Setup", icon='COLOR')
			row.operator(operators.BGE_PT_debug_lines.bl_idname, text="Draw", icon='GREASEPENCIL')


		col = box.column(align=True)

		row = col.row(align=True)
		if context.scene.BGE_Settings.path == "":
			row.alert = True
		row.prop(context.scene.BGE_Settings, "path", text="")
		if context.scene.BGE_Settings.path != "":
			row = row.row(align=True)
			row.operator("wm.path_open", text="", icon='FILE_TICK').filepath = context.scene.BGE_Settings.path

		row = col.row(align=True)
		row.prop(context.scene.BGE_Settings, "mode_bundle", text="Bundle by", icon='GROUP')
		row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_bundle"


		row = col.row(align=True)
		row.prop(context.scene.BGE_Settings, "mode_pivot", text="Pivot at", icon='OUTLINER_DATA_EMPTY', expand=False)
		row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_pivot"


		col = box.column(align=True)
		row = col.row(align=True)
		row.prop(context.scene.BGE_Settings, "padding", text="Padding", expand=True)
		row.prop(context.scene.BGE_Settings, "include_children", text="Include children", expand=True)

		# Warnings

		if context.space_data.local_view:
			box = col.box()
			box.label(text="Can't export in local view mode.", icon='CANCEL')

		if context.active_object and context.active_object.mode != 'OBJECT':
			box = col.box()
			box.label(text="Requires object mode to export.", icon='CANCEL')

		if context.scene.BGE_Settings.path == "":
			box = col.box()
			box.label(text="No output path defined.", icon='CANCEL')

		elif mode not in platforms.platforms:
			box = col.box()
			box.label(text="Platform not implemented", icon='CANCEL')
		
		elif context.scene.BGE_Settings.mode_bundle == 'COLLECTION' and len(bpy.data.collections) == 0:
			box = col.box()
			box.label(text="No groups available", icon='CANCEL')

		elif not platforms.platforms[mode].is_valid()[0]:
			box = col.box()
			box.label(text=platforms.platforms[mode].is_valid()[1], icon='CANCEL')			
		
		


class BGE_PT_tools_panel(bpy.types.Panel):
	bl_idname = "BGE_PT_tools_panel"
	bl_label = "Tools"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Game Exporter"
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		
		# Get bundles
		#bundles = objects_organise.get_bundles()

		row = col.row(align=True)
		row.scale_y = 1.85
		row.operator(operators.BGE_OT_fence_draw.bl_idname, text="Draw Fences", icon='AXIS_TOP')
		row.operator(operators.BGE_OT_fence_clear.bl_idname, text="", icon='PANEL_CLOSE')

		col.separator()

		col = col.column(align=True)

		col.operator(operators.BGE_OT_pivot_ground.bl_idname, text="Pivot at Ground", icon='OUTLINER_DATA_EMPTY')
		col.operator(operators.BGE_OT_tool_geometry_fix.bl_idname, text="Fix imp. Geometry", icon='MESH_ICOSPHERE')
		
		if bpy.app.debug_value != 0:
			col.operator(operators.BGE_OT_tool_pack_bundles.bl_idname, text="Pack & Arrange", icon='UGLYPACKAGE')
		


			row = layout.row(align=True)
			row.alert =True
			row.operator(operators.BGE_OT_fence_clear.bl_idname, text="Pack", icon='IMGDISPLAY')
			row.operator(operators.BGE_OT_fence_clear.bl_idname, text="Align Z", icon='TRIA_DOWN_BAR')
			layout.separator()





class BGE_PT_modifiers_panel(bpy.types.Panel):
	bl_idname = "BGE_PT_modifiers_panel"
	bl_label = "Modifiers"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Game Exporter"
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()

		for modifier in modifiers.modifiers:
			box = col.box()
			modifier.draw(box)

		r = col.row()
		r.enabled = False

		count = 0
		for modifier in modifiers.modifiers:
			if modifier.get("active"):
				count+=1

		if count > 0:
			r.label(text="{}x modifiers are applied upon export".format(count))


class BGE_PT_files_panel(bpy.types.Panel):
	bl_idname = "BGE_PT_files_panel"
	bl_label = "Bundles"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Game Exporter"
	bl_context = "objectmode"
	# bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout
		
		# Get bundles
		bundles = objects_organise.get_bundles()

		icon = icons.icon_get(bpy.context.scene.BGE_Settings.target_platform.lower())


		col = layout.column(align=True)	
		row = col.row(align=True)

		split = row.split(factor=0.4, align=True)

		c = split.column(align=True)
		c.scale_y = 1.85
		c.operator(operators.BGE_OT_file_import.bl_idname, text="Import", icon='IMPORT')
		
		c = split.column(align=True)
		c.scale_y = 1.85
		c.operator(operators.BGE_OT_file_export.bl_idname, text="Export {}x".format(len(bundles)), icon_value=icon)
		

		if len(bpy.context.scene.BGE_Settings.recent) > 0:
			if len(objects_organise.recent_load_objects()) > 0:
				row = col.row(align=True)
				row.scale_y = 1.3

				r = row.row(align=True)
				r.operator(operators.BGE_OT_export_recent.bl_idname, text=objects_organise.recent_get_label(), icon='RECOVER_LAST')
				
				r = r.row(align=True)
				# r.alert = True
				r.operator(operators.BGE_OT_export_recent_clear.bl_idname, text="", icon='X')



		layout.separator()

		
		mode = bpy.context.scene.BGE_Settings.target_platform

		
		if(len(bundles) > 0):
			# box_files = layout.box()
			# box_files.active = False
			row = layout.row()
			if len(bundles) == 1:
				row.label(text = "1x Bundle")
			else:
				row.label(text = "{}x Bundles".format(len(bundles)))

			row.prop(context.scene.BGE_Settings, "collapseBundles", text="Compact", expand=True)


			folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.BGE_Settings.path ))

			# Display bundles
			for fileName,data in bundles.items():
				objects = data['objects']
				helpers = data['helpers']

				# row = layout.row(align=True)
				box = layout.box()
				# box.scale_y = 0.8
				column = box.column(align=True)

				row = column.row(align=True)
				if(fileName == "unknown"):
					row.alert = True

				# Process object name via modifiers
				path_folder = folder
				path_name = fileName
				for modifier in modifiers.modifiers:
					if modifier.get("active"):
						path_folder = modifier.process_path(path_name, path_folder)
						path_name = modifier.process_name(path_name)
	
				label = fileName
				if mode in platforms.platforms:
					label = platforms.platforms[mode].get_filename(path_name)

				if(len(objects) > 1):
					label = "{}  {}x".format(label, len(objects));

				row.operator(operators.BGE_OT_select.bl_idname,icon_value=icon, emboss=False, text=label).key = fileName
				r = row.row(align=True)
				r.alert = True
				r.operator(operators.BGE_OT_remove.bl_idname,text="", icon='X').key = fileName

				if not context.scene.BGE_Settings.collapseBundles:
					box = box.box()
					for i in range(0,len(objects)):
						row = box.row(align=True)
						row.label(text=objects[i].name)

				if helpers and not context.scene.BGE_Settings.collapseBundles:
					box = box.box()
					for i in range(0,len(helpers)):
						row = box.row(align=True)
						row.label(text=helpers[i].name)



addon_keymaps = []
classes = [BGE_Settings, BGE_PT_core_panel, BGE_PT_tools_panel, BGE_PT_modifiers_panel, BGE_PT_files_panel]

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	bpy.types.Scene.BGE_Settings = bpy.props.PointerProperty(type=BGE_Settings)

	# Register modifier settings
	for modifier in modifiers.modifiers:
		print("register modifier: {}".format(modifier.__module__))
		modifier.register()

	for operator in operators.operators:
		print("register operator: {}".format(operator))
		register_class(operator)


	# handle the keymap
	km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
	kmi = km.keymap_items.new(operators.BGE_OT_file_export.bl_idname, 'E', 'PRESS', ctrl=True, shift=False)
	kmi = km.keymap_items.new(operators.BGE_OT_export_recent.bl_idname, 'E', 'PRESS', ctrl=True, shift=True)
	# kmi.properties.total = 4
	addon_keymaps.append(km)


def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		try:
			unregister_class(cls)
		except:
			print(cls)

	#Unregister Settings
	del bpy.types.Scene.BGE_Settings

	# Unregister modifier settings
	for modifier in modifiers.modifiers:
		modifier.unregister()

	for operator in operators.operators:
		unregister_class(operator)

	# handle the keymap
	for km in addon_keymaps:
		bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)
	del addon_keymaps[:]

