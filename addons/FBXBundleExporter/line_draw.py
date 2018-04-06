import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math


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



	def add_lines(self, lines, dash=0.0):
		for line in lines:
			self.add_line(line, mode)


	def add_line(self, points, dash=0.0):
		print("Line")
		stroke = self.get_gp_stroke()
		offset = len(stroke.points)

		stroke.points.add(len(points))
		for i in range(len(points)):
			index = offset+i
			stroke.points[index].co = points[i]
			stroke.points[index].select   = True
			stroke.points[index].pressure = 1
			stroke.points[index].strength = 1


	def add_text(self, text, pos=Vector((0,0,0)), size=1.0):
		print("text")
		text = text.upper()
		size_xy = Vector((0.66,1)) * size
		padding = size_xy.x/2

		offset = 0

		def add_character(strokes):
			nonlocal offset

			print("Str {} = {}x".format(char, len(strokes)))
			for stroke in strokes:
				path = []
				for id in stroke:
					x = (id % 3) * (size_xy.x/2) + (offset * (size_xy.x*1.5)) + padding
					y = math.floor(id/3) * size_xy.y/2 + padding
					path.append(pos + Vector((x,-size_xy.y-2* padding + y,0)))
				
				# add_mesh_edges(bm, path)
				self.add_line(path)

		# Grid Font: https://image.shutterstock.com/z/stock-vector-set-of-font-design-base-on-line-and-dot-which-represent-connection-link-and-network-vector-621619463.jpg			
		
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
