import bpy

from . import bundle
from . import exporter

Bundle = bundle.Bundle


def is_object_valid(obj):
	# Objects to include in a bundle as 'export-able'
	if obj.hide_viewport:
		return False
		
	return True

def get_key(obj, mode_bundle):
	if mode_bundle == 'NAME':
		name = obj.name
		# Remove blender naming digits, e.g. cube.001, cube.002,...
		if len(name)>= 4 and name[-4] == '.' and name[-3].isdigit() and name[-2].isdigit() and name[-1].isdigit():
			name = name[:-4]
		return name

	elif mode_bundle == 'PARENT':
		if obj.parent:
			limit = 100
			obj_parent = obj.parent
			for i in range(limit):
				if obj_parent.parent:
					obj_parent = obj_parent.parent
				else:
					break
			return obj_parent.name
		else:
			return obj.name

	elif mode_bundle == 'COLLECTION':
		if len(obj.users_collection) >= 1:
			return obj.users_collection[0].name

	elif mode_bundle == 'SCENE':
		return bpy.context.scene.name

	return "UNDEFINED"

def get_bundles():
    return [x for x in bpy.context.scene.BGE_Settings.bundles]

def create_bundles_from_selection():
    mode_bundle = bpy.context.scene.BGE_Settings.mode_bundle
    mode_pivot = bpy.context.scene.BGE_Settings.mode_pivot
    objects = [obj for obj in bpy.context.selected_objects]
    keys = set()
    for x in objects:
        keys.add(get_key(x, mode_bundle))

    for key in keys:
        if not any([x.key == key for x in get_bundles()]):
            bundle = bpy.context.scene.BGE_Settings.bundles.add()
            bundle.key = key
            bundle.mode_bundle = mode_bundle
            bundle.mode_pivot = mode_pivot