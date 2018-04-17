import bpy, bmesh
import os
import mathutils
from mathutils import Vector

from . import objects_organise

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_copy_unity_script"
	bl_label = "Copy Unity Script"
	bl_description = "Copy Unity editor script to folder"

	filepath = bpy.props.StringProperty(subtype="FILE_PATH")


	def invoke(self, context, event):
		if self.filepath == "":
			self.filepath = bpy.context.scene.FBXBundleSettings.path

		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}


	def draw(self, context):
		layout = self.layout

		col = layout.column()
		col.label(text="Custom Interface!_________")
		col.prop(self, "filepath")


	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		copy_script(self.filepath)
		return {'FINISHED'}



def copy_script(path):
	# https://blenderapi.wordpress.com/2011/09/26/file-selection-with-python/

	print("Path {}".format(path))
	pass

	'''
import bpy
import struct
 
class CustomDrawOperator(bpy.types.Operator):
    bl_idname = "object.custom_draw"
    bl_label = "Import"
 
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
 
    my_float = bpy.props.FloatProperty(name="Float")
    my_bool = bpy.props.BoolProperty(name="Toggle Option")
    my_string = bpy.props.StringProperty(name="String Value")
 
    def execute(self, context):
        print()
        return {'FINISHED'}
 
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
 
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Custom Interface!")
 
        row = col.row()
        row.prop(self, "my_float")
        row.prop(self, "my_bool")
 
        col.prop(self, "my_string")
 
bpy.utils.register_class(CustomDrawOperator)
 
# test call
bpy.ops.object.custom_draw('INVOKE_DEFAULT')
'''





	
	
	# path = bpy.path.abspath(path)



	# filenames = sorted(os.listdir(path))
	# filenames = [name for name in filenames if (name.lower().endswith('.fbx') or name.lower().endswith('.obj') )]


	# for name in filenames:
	# 	file_path = os.path.join(path, name)
	# 	extension = (os.path.splitext(file_path)[1])[1:].lower()
	# 	print("- {} = {}".format(extension, file_path))

	# 	# https://docs.blender.org/api/2.78a/bpy.ops.import_scene.html
	# 	if extension == 'fbx':
	# 		bpy.ops.import_scene.fbx(filepath = file_path)
	# 	elif extension == 'obj':
	# 		bpy.ops.import_scene.obj(filepath = file_path)

