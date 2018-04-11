if "bpy" in locals():
	import imp
	imp.reload(gp_draw)
	imp.reload(objects_organise)
	imp.reload(op_file_export)
	imp.reload(op_file_import)
	imp.reload(op_fence_draw)
	imp.reload(op_fence_clear)
else:
	from . import gp_draw
	from . import objects_organise
	from . import op_file_export
	from . import op_file_import
	from . import op_fence_draw
	from . import op_fence_clear

import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math


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
	padding = bpy.props.FloatProperty (
		name="Padding",
		default=0.5,
		min = 0,
		description="Padding for fences or Space bundling",
		subtype='DISTANCE'
	)
	mode_bundle = bpy.props.EnumProperty(items= 
		[('NAME', 'Name', "Group by matching names"), 
		('SPACE', 'Space', "Group by shared space"), 
		('GROUP', 'Group', "Group by 'Groups'")
		], name = "Bundle Mode", default = 'NAME'
	)
	mode_pivot = bpy.props.EnumProperty(items=[
		('OBJECT_FIRST', 'First Name', "First object sorted by name of the group"), 
		('OBJECT_LOWEST', 'Lowest Object', "The Scene center 0,0,0'"),
		('BOUNDS_BOTTOM', 'Bottom Center', "Bottom center of the bounds of the group"), 
		('SCENE', 'Scene 0,0,0', "The Scene center 0,0,0'")
		], name = "Pivot From", default = 'OBJECT_FIRST'
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



		
		if bpy.app.debug_value != 0:
			row = box.row(align=True)
			row.alert = True
			row.operator(op_debug_setup.bl_idname, text="Setup Debug", icon='IMPORT')




		row = box.row()
		if context.scene.FBXBundleSettings.path == "":
			row.alert = True
		row.prop(context.scene.FBXBundleSettings, "path", text="")
		
		col = box.column(align=True)
		row = col.row(align=True)
		row.prop(context.scene.FBXBundleSettings, "mode_bundle", text="", icon='SURFACE_NCYLINDER')
		row.prop(context.scene.FBXBundleSettings, "mode_pivot", text="", icon='OUTLINER_OB_EMPTY', expand=False)
		
		col.prop(context.scene.FBXBundleSettings, "padding", text="Padding", expand=False)
		

		# layout.separator()
		
		# layout.label(text="Add Modifier")
		# box = layout.box()
		# box.label(text="[] Copy Modifiers")
		# box.label(text="[] Merge to single Mesh")
		layout.separator()
		# Get bundles
		bundles = objects_organise.get_bundles()

		# row = layout.row()
		# row.label('Files: '+str(len(bundles))+"x")
		
		col = layout.column(align=True)

		

		row = col.row(align=True)
		row.operator(op_fence_draw.op.bl_idname, text="Draw Fence", icon='STICKY_UVS_LOC')
		row.operator(op_fence_clear.op.bl_idname, text="", icon='PANEL_CLOSE')
		
		# Debug Tools
		if bpy.app.debug_value != 0:
			row = col.row(align=True)
			row.alert =True
			row.operator(op_debug_lines.bl_idname, text="Draw Debug")

		col = layout.column(align=True)	
		row = col.row(align=True)
		row.scale_y = 1.7
		row.operator(op_file_export.op.bl_idname, text="Export {}x".format(len(bundles)), icon='EXPORT')
		row = col.row(align=True)
		row.operator(op_file_import.op.bl_idname, text="Import Objects", icon='IMPORT')
	
		
		
		
		layout.separator()

		if bpy.app.debug_value != 0:
			box = layout.box()
			box.alert =True
			box.label(text="Align")
			row = box.row(align=True)
			row.operator(op_fence_clear.op.bl_idname, text="Pack Bundles")
			row.operator(op_fence_clear.op.bl_idname, text="Ground Z")


		
		if(len(bundles) > 0):

			for fileName,objects in bundles.items():

				# row = layout.row(align=True)
				box = layout.box()
				# box.scale_y = 0.8
				column = box.column(align=True)

				row = column.row(align=True)
				if(fileName == "unknown"):
					row.alert = True
				
				row.operator(op_select.bl_idname,icon='MOD_SOLIDIFY', text="{}.fbx".format(fileName)).key = fileName
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





class op_import(bpy.types.Operator):
	bl_idname = "fbxbundle.import"
	bl_label = "Import"

	def execute(self, context):
		objects_io.import_objects()
		return {'FINISHED'}



class op_export(bpy.types.Operator):
	bl_idname = "fbxbundle.export"
	bl_label = "Export"

	@classmethod
	def poll(cls, context):
		if len(bpy.context.selected_objects) > 0:
			return True
		return False

	def execute(self, context):
		objects_io.export_objects()
		return {'FINISHED'}





# registers
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.FBXBundleSettings = bpy.props.PointerProperty(type=FBXBundleSettings)

def unregister():
	bpy.utils.unregister_class(FBXBundleExporterPanel)
	del bpy.types.Scene.FBXBundleSettings


if __name__ == "__main__":
	register()

	


