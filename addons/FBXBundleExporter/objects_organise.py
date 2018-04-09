import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math
import random
import re


def get_objects():
	objects = []
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			objects.append(obj)

	return sort_objects_name(objects)



def sort_objects_name(objects):
	names = {}
	for obj in objects:
		names[obj.name] = obj

	# now sort
	sorted_objects = []
	for key in sorted(names.keys()):
		sorted_objects.append(names[key])

	return sorted_objects



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



def get_pivot(objects, bounds):
	mode_pivot = bpy.context.scene.FBXBundleSettings.mode_pivot

	print("Get pivot {}x : {}".format(len(objects), mode_pivot))
	if mode_pivot == 'NAME_FIRST':
		if len(objects) > 0:
			return objects[0].location

	elif mode_pivot == 'BOUNDS_BOTTOM':
		return Vector((
			bounds.min.x + bounds.size.x/2,
			bounds.min.y + bounds.size.y/2,
			bounds.min.z
		))

	elif mode_pivot == 'SCENE':
		return Vector((0,0,0))

	# Default
	return Vector((0,0,0))



def get_key(obj):
	mode_bundle = bpy.context.scene.FBXBundleSettings.mode_bundle

	if mode_bundle == 'NAME':
		name = obj.name
		# Remove blender naming digits, e.g. cube.001, cube.002,...
		if len(name)>= 4 and name[-4] == '.' and name[-3].isdigit() and name[-2].isdigit() and name[-1].isdigit():
			name = name[:-4]

		# Split Camel Case
		split = re.sub('(?!^)([A-Z][a-z]+)', r' \1', name).split()
		name = '_'.join(split)

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


	elif mode_bundle == 'GROUP':
		if len(obj.users_group) >= 1:
			return obj.users_group[0].name


	elif mode_bundle == 'SPACE':
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



class ObjectBounds:
	obj = None
	min = Vector((0,0,0))
	max = Vector((0,0,0))
	size = Vector((0,0,0))
	center = Vector((0,0,0))

	def __init__(self, obj):
		self.obj = obj
		corners = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]

		self.min = Vector((corners[0].x, corners[0].y, corners[0].z))
		self.max = Vector((corners[0].x, corners[0].y, corners[0].z))
		for corner in corners:
			self.min.x = min(self.min.x, corner.x)
			self.min.y = min(self.min.y, corner.y)
			self.min.z = min(self.min.z, corner.z)
			self.max.x = max(self.max.x, corner.x)
			self.max.y = max(self.max.y, corner.y)
			self.max.z = max(self.max.z, corner.z)

		self.size = self.max - self.min
		self.center = self.min+(self.max-self.min)/2


	def combine(self, other):
		self.min.x = min(self.min.x, other.min.x)
		self.min.y = min(self.min.y, other.min.y)
		self.min.z = min(self.min.z, other.min.z)
		self.max.x = max(self.max.x, other.max.x)
		self.max.y = max(self.max.y, other.max.y)
		self.max.z = max(self.max.z, other.max.z)

		self.size = self.max - self.min
		self.center = self.min+(self.max-self.min)/2

	def is_colliding(self, other):
		def is_collide_1D(A_min, A_max, B_min, B_max):
			# One line is inside the other
			length_A = A_max-A_min
			length_B = B_max-B_min
			center_A = A_min + length_A/2
			center_B = B_min + length_B/2
			return abs(center_A - center_B) <= (length_A+length_B)/2

		collide_x = is_collide_1D(self.min.x, self.max.x, other.min.x, other.max.x)
		collide_y = is_collide_1D(self.min.y, self.max.y, other.min.y, other.max.y)
		collide_z = is_collide_1D(self.min.z, self.max.z, other.min.z, other.max.z)
		return collide_x and collide_y and collide_z