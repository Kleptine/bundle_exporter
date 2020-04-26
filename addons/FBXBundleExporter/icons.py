import os

import bpy

preview_icons = None
icons = ["unity.png", "unreal.png", "blender.png","gltf.png"]

def icon_get(name):
	if name not in preview_icons:
		print("Icon '{}' not found ".format(name))
	return preview_icons[name].icon_id


def icon_register(fileName):
	name = fileName.split('.')[0]   # Don't include file extension
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	preview_icons.load(name, os.path.join(icons_dir, fileName), 'IMAGE')

def unregister():
	global preview_icons
	bpy.utils.previews.remove(preview_icons)
	preview_icons = None

def register ():
	global preview_icons
	preview_icons = bpy.utils.previews.new()

	for icon in icons:
		icon_register(icon)
	
