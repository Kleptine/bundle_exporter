import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math
import random
import operator

from . import objects_organise


_draw = None

def get_draw():
	global _draw
	if _draw == None:
		_draw = LineDraw("fence",(0,0.8,1.0))
	return _draw



def clear():
	draw = get_draw()
	draw.clear()



def draw_debug():
	# test_grease_pencil()
	padding = bpy.context.scene.FBXBundleSettings.padding

	draw = get_draw()
	draw.clear()

	draw.add_text("ABCDEFGHIJKLM", Vector((0,0,0)), padding)
	draw.add_text("NOPQRSTUVWXYZ", Vector((0,-1,0)), padding)
	draw.add_text("0123456789", Vector((0,-2,0)), padding)
	draw.add_text("~!@#$%^&*()", Vector((0,-3,0)), padding)
	draw.add_text("_-+\"';:,.<>[](){}\\/?", Vector((0,-4,0)), padding)
	draw.add_text("www.renderhjs.net", Vector((0,-5,0)), padding)

	for i in range(1,5):
		draw.add_circle(Vector((4,-4-6,0)), i, i*4)



def draw_bounds(name, objects, bounds):
	print("Fence {}".format(name))

	padding = bpy.context.scene.FBXBundleSettings.padding
	
	
	pos = bounds.center

	_min = bounds.min
	_max = bounds.max
	_min-= Vector((padding,padding,0))
	_max+= Vector((padding,padding,0))
	size = _max - _min

	# Bounds
	draw = get_draw()
	draw.add_line(
		[_min +Vector((0,0,0)),
		_min +Vector((size.x,0,0)),
		_min +Vector((size.x,size.y,0)),
		_min +Vector((0,size.y,0)),
		_min +Vector((0,0,0))]
	)
	draw.add_line([_min +Vector((0,0,0)), _min +Vector((0,0,padding))] )
	draw.add_line([_min +Vector((size.x,0,0)), _min +Vector((size.x,0,padding))] )
	draw.add_line([_min +Vector((size.x,size.y,0)), _min +Vector((size.x,size.y,padding))] )
	draw.add_line([_min +Vector((0,size.y,0)), _min +Vector((0,size.y,padding))] )


	# Text
	label = name
	if len(objects) > 1:
		label = "{} {}x".format(name, len(objects))
	draw.add_text(label, _min, padding)

	# Draw pole + Flag
	pivot = objects_organise.get_pivot(objects, bounds)
	height = max(padding, size.z)*2.0
	draw.add_line( [ Vector((pivot.x, pivot.y, _min.z)), Vector((pivot.x, pivot.y,_min.z+height))], dash=padding*0.2)
	draw.add_line( [
		Vector((pivot.x, pivot.y, _min.z + height - padding)),
		Vector((pivot.x - padding, pivot.y - padding, _min.z + height - padding/2)),
		Vector((pivot.x, pivot.y, _min.z + height))
	] )
	draw.add_circle( Vector((pivot.x, pivot.y, _min.z)), padding, sides=8)
	
	# Grid lines
	draw_grid(objects, bounds)

				# print("Collide {}".format(  ))

	# draw.add_box( Vector((b.min.x, bounds.min.y, bounds.min.z)), padding*0.25)
		# draw.add_box( Vector((b.max.x, bounds.min.y, bounds.min.z)), padding*0.25)
	


def draw_grid(objects, bounds_group):
	draw = get_draw()
	padding = bpy.context.scene.FBXBundleSettings.padding

	bounds_objects = {}
	for o in objects:
		bounds_objects[o] = objects_organise.ObjectBounds(o)

	grid_x = SortedGridAxis(objects, bounds_objects, 'x') 
	grid_y = SortedGridAxis(objects, bounds_objects, 'y') 

	# Draw grids
	for i in range(len(grid_x.groups)-1):
		A = grid_x.bounds[i][1] #End first item
		B = grid_x.bounds[i+1][0] #Start next item
		center = A + (B-A)/2

		draw.add_line([
			Vector((center, bounds_group.min.y, bounds_group.min.z+padding)),
			Vector((center, bounds_group.min.y, bounds_group.min.z)),
			Vector((center, bounds_group.max.y, bounds_group.min.z)),
			Vector((center, bounds_group.max.y, bounds_group.min.z+padding))
		], alpha=0.33)

	for i in range(len(grid_y.groups)-1):
		A = grid_y.bounds[i][1] #End first item
		B = grid_y.bounds[i+1][0] #Start next item
		center = A + (B-A)/2

		draw.add_line([
			Vector((bounds_group.min.x, center, bounds_group.min.z+padding)),
			Vector((bounds_group.min.x, center, bounds_group.min.z)),
			Vector((bounds_group.max.x, center, bounds_group.min.z)),
			Vector((bounds_group.max.x, center, bounds_group.min.z+padding))
		], alpha=0.33)

	# Draw grids
	# for i in range(len(grid_x.groups)):
	# 	A = grid_x.bounds[i][0]
	# 	B = grid_x.bounds[i][1]
	# 	# center = A + (B-A)/2
	# 	# center = grid_x.bounds[i][0]

	# 	draw.add_line([
	# 		Vector((A, bounds_group.min.y, bounds_group.min.z)),
	# 		Vector((A, bounds_group.max.y, bounds_group.min.z))
	# 	], padding)

	# 	draw.add_line([
	# 		Vector((B, bounds_group.min.y, bounds_group.min.z)),
	# 		Vector((B, bounds_group.max.y, bounds_group.min.z))
	# 	], padding)


	# 	draw.add_text(str(i)+"A", Vector((A, bounds_group.min.y-padding*1.5, bounds_group.min.z)), padding*0.5)
	# 	draw.add_text(str(i)+"B", Vector((B, bounds_group.min.y-padding*1.5, bounds_group.min.z)), padding*0.5)

	


class SortedGridAxis:
	groups = []
	bounds = []

	def __init__(self, objects, bounds, axis_var='x'):
		self.groups = [[o] for o in objects]
		self.bounds = [[getattr(bounds[o].min, axis_var), getattr(bounds[o].max, axis_var)] for o in objects]
		# self.setup_gp()

		# Calculate clusters

		for i in range(len(self.groups)):
			print("i {}. / {}".format(i, len(self.groups)))

			j = 0
			for x in range(len(self.groups)):
				print("  j {}. / {}".format(j, len(self.groups)))

				if i != j and i < len(self.groups) and j < len(self.groups):
					g0 = self.groups[i]
					g1 = self.groups[j]
					b0 = self.bounds[i]
					b1 = self.bounds[j]
					# if g0 not in processed:
					if self.is_collide(b0[0], b0[1], b1[0], b1[1]):
						for o in g1:
							g0.append(o)
						b0[0] = min(b0[0], b1[0])
						b0[1] = max(b0[1], b1[1])
						self.groups.remove(g1)
						self.bounds.remove(b1)
						j-=1
						print("    Grp @ {} {} = {}x".format(i,j,len(self.groups)))
						# break
						# j-=1
						# i-=1
						# processed.append(g0)
				j+=1
			# 	j+=1
			# i+=1


		print("Final {} x {}".format(len(self.groups), len(self.bounds)))
		
		# Sort
		values = {(self.bounds.index(b)):(b[0]) for b in self.bounds}
		ordered = sorted(values.items(), key=operator.itemgetter(1))
		if len(self.groups) > 1:
			copy_groups = self.groups.copy()
			copy_bounds = self.bounds.copy()

			index = 0
			for s in ordered:
				print(".. Sorted {} = {}".format(s[0], s[1]))
				self.groups[index] = copy_groups[ s[0] ]
				self.bounds[index] = copy_bounds[ s[0] ]
				index+=1


	def is_collide(self, A_min, A_max, B_min, B_max):
		# One line is inside the other
		length_A = A_max-A_min
		length_B = B_max-B_min
		center_A = A_min + length_A/2
		center_B = B_min + length_B/2
		return abs(center_A - center_B) <= (length_A+length_B)/2



class LineDraw:
	
	name = ""
	color = (0,0,0)

	gp = None
	gp_layer = None
	gp_palette = None
	gp_color = None
	gp_frame = None


	def __init__(self, name, color):
		self.name = name
		self.color = color
		self.setup_gp()


	def clear(self):
		self.gp_frame.clear()


	def add_box(self, position, size=1.0):
		print("Box")

		self.add_line([
			position + Vector((-0.5,-0.5,-0.5)) * size,
			position + Vector((+0.5,-0.5,-0.5)) * size,
			position + Vector((+0.5,+0.5,-0.5)) * size,
			position + Vector((-0.5,+0.5,-0.5)) * size,
			position + Vector((-0.5,-0.5,-0.5)) * size,
		])
		self.add_line([
			position + Vector((-0.5,-0.5,-0.5)) * size,
			position + Vector((-0.5,-0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((+0.5,-0.5,-0.5)) * size,
			position + Vector((+0.5,-0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((+0.5,+0.5,-0.5)) * size,
			position + Vector((+0.5,+0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((-0.5,+0.5,-0.5)) * size,
			position + Vector((-0.5,+0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((-0.5,-0.5,+0.5)) * size,
			position + Vector((+0.5,-0.5,+0.5)) * size,
			position + Vector((+0.5,+0.5,+0.5)) * size,
			position + Vector((-0.5,+0.5,+0.5)) * size,
			position + Vector((-0.5,-0.5,+0.5)) * size,
		])


	def add_cross(self, position, size=1.0):
		print("...")


	def add_circle(self, position, radius = 1, sides = 8):

		for i in range(sides):
			a0 = ((i+0) * (360 / sides))*math.pi/180
			a1 = ((i+1) * (360 / sides))*math.pi/180
			A = position + Vector((math.cos(a0), math.sin(a0), 0))*radius
			B = position + Vector((math.cos(a1), math.sin(a1), 0))*radius
			self.add_line([A,B])




	def add_lines(self, lines, alpha=1.0, dash=0.0):
		for line in lines:
			self.add_line(line, alpha, dash)


	def add_line(self, points, alpha=1.0, dash=0.0):
		stroke = self.get_gp_stroke()
		offset = len(stroke.points)

		stroke.points.add(len(points))
		for i in range(len(points)):
			index = offset+i
			stroke.points[index].co = points[i]
			stroke.points[index].select   = True
			stroke.points[index].pressure = 1
			stroke.points[index].strength = alpha


	def add_text(self, text, pos=Vector((0,0,0)), size=1.0):
		text = text.upper()
		size_xy = Vector((0.66,1)) * size
		padding = size_xy.x/2

		offset = 0

		def add_character(strokes):
			nonlocal offset

			for stroke in strokes:
				path = []
				for id in stroke:
					x = (id % 3) * (size_xy.x/2) + (offset * (size_xy.x*1.5)) + padding
					y = math.floor(id/3) * size_xy.y/2 + padding
					path.append(pos + Vector((x,-size_xy.y-2* padding + y,0)))
				
				# add_mesh_edges(bm, path)
				self.add_line(path)

		# 6 -- 7 -- 8
		# |    |    |
		# 3 -- 4 -- 5
		# |    |    |
		# 0 -- 1 -- 2
		chars = {
			# Alhabet Uppercase
			'A':[[0,3,7,5,2],[3,5]],
			'B':[[0,6,8,4,2,0],[3,4]],
			'C':[[2,1,3,7,8]],
			'D':[[0,6,7,5,1,0]],
			'E':[[2,0,6,8],[3,4]],
			'F':[[0,6,8],[3,4]],
			'G':[[4,5,2,0,3,7,8]],
			'H':[[0,6],[3,5],[2,8]],
			'I':[[0,2],[1,7],[6,8]],
			'J':[[6,8,5,1,0,3]],
			'K':[[6,0],[3,4,8],[4,2]],
			'L':[[6,0,2]],
			'M':[[0,6,4,8,2]],
			'N':[[0,6,2,8]],
			'O':[[1,3,7,5,1]],
			'P':[[0,6,7,5,3]],
			'Q':[[1,3,7,5,1],[4,2]],
			'R':[[0,6,8,4,2],[3,4]],
			'S':[[0,1,5,3,7,8]],
			'T':[[6,8],[7,1]],
			'U':[[6,0,2,8]],
			'V':[[6,3,1,5,8]],
			'W':[[6,0,4,2,8]],
			'X':[[6,2],[0,8]],
			'Y':[[6,4,8],[4,1]],
			'Z':[[6,8,0,2]],


			# Special
			' ':[],
			'.':[[1,2]],
			'+':[[3,5],[7,1]],
			'-':[[3,5]],
			'_':[[0,2]],
			'|':[[1,7]],
			'/':[[0,8]],
			'\\':[[6,2]],
			'\'':[[7,4]],
			'*':[[0,8],[3,5],[6,2],[1,7]],
			'%':[[6,3],[8,0],[5,2]],
			'"':[[6,4],[7,5]],
			'~':[[3,7,4,8]],
			'@':[[0,6,8,2,1,4]],
			'$':[[0,1,5,3,7,8],[7,1]],
			'^':[[3,7,5]],
			# ';':[[7,8],[4,0]],
			':':[[1,2],[4,5]],
			# '&':[[2,3,6,7,4,3,0,5]],

			# Pairs
			'(':[[1,3,7]],
			')':[[7,5,1]],
			'[':[[7,6,0,1]],
			']':[[7,8,2,1]],
			'<':[[8,3,2]],
			'>':[[6,5,0]],
			

			# Numbers
			'0':[[6,8,2,0,6],[0,8]],		
			'1':[[0,2],[1,7,6]],
			'2':[[6,7,5,3,0,2]],
			'3':[[6,8,4,2,0]],
			'4':[[6,3,5],[8,2]],
			'5':[[8,6,3,5,1,0]],
			'6':[[8,7,3,0,2,5,3]],
			'7':[[3,6,8,5,1]],
			'8':[[6,2,0,8,6]],
			'9':[[5,3,6,8,5,1,0]],
			
			# Unknown
			'?':[[3,6,8,5,4,1]]
		}
		for char in text:
			if char in chars:
				add_character(chars[char])
			else:
				# unknown character
				add_character(chars['?'])
			offset+=1


	def setup_gp(self):
		id_grease = "id_grease"
		id_layer = "id_layer"
		id_palette = "id_palette"

		# 
		bpy.context.space_data.show_grease_pencil = True

		# Grease Pencil
		if id_grease in bpy.data.grease_pencil:
			self.gp = bpy.data.grease_pencil.get(id_grease, None)
		else:
			self.gp = bpy.data.grease_pencil.new(id_grease)
		bpy.context.scene.grease_pencil = self.gp

		# Layer
		if id_layer in self.gp.layers:
			self.gp_layer = self.gp.layers[id_layer]
		else:
			self.gp_layer = self.gp.layers.new(id_layer, set_active=True)
		self.gp_layer.show_x_ray = False

		# Palette
		if id_palette in self.gp.palettes:
			self.gp_palette = self.gp.palettes.get(id_palette)
		else:
			self.gp_palette = self.gp.palettes.new(id_palette, set_active=True)

		# Color
		if len(self.gp_palette.colors) > 0:
			self.gp_color = self.gp_palette.colors[0]
		else:
			self.gp_color = self.gp_palette.colors.new()
			self.gp_color.color=(0,0.8,1)
		
		# Frame
		if len(self.gp_layer.frames) == 0:
			self.gp_frame = self.gp_layer.frames.new(bpy.context.scene.frame_current)
		else:
			self.gp_frame = self.gp_layer.frames[0]


	def get_gp_stroke(self, id_grease="fance", id_layer="lines", id_palette="colors"):
		stroke  = self.gp_frame.strokes.new(colorname=self.gp_color.name)
		stroke.draw_mode = '3DSPACE'
		return stroke
