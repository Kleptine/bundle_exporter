import bpy
import os
import mathutils
from mathutils import Vector
import math
import random


_draw = None


def get_draw():
    global _draw
    if not _draw or not _draw.is_valid():
        _draw = LineDraw("fence", (0, 0.8, 1.0))
    return _draw


def clear():
    draw = get_draw()
    draw.clear()


def draw_debug():
    # test_grease_pencil()
    padding = bpy.context.scene.BGE_Settings.padding

    draw = get_draw()
    draw.clear()

    step = 0

    def add_text(step, text):
        draw.add_text(text, Vector((0, -step, 0)), padding)
        return step + 1

    step = add_text(step, "abcdefghijklm")
    step = add_text(step, "nopqrstuvwxyz")

    step = add_text(step, "ABCDEFGHIJKLM")
    step = add_text(step, "NOPQRSTUVWXYZ")

    step = add_text(step, "0123456789")
    step = add_text(step, "~!@#$%^&*()")
    step = add_text(step, "_-+\"';:,.<>[](){}\\/?")
    step = add_text(step, "www.renderhjs.net")

    # Draw circles
    # for i in range(1,8):
    # 	draw.add_circle(Vector((4,4,0)), i*0.5, i*3)


class LineDraw:
    """
    Grease Pencil v3 drawing class for Blender 4.3+
    Replaces the legacy annotations system
    """

    name = ""
    color = (0, 0, 0)

    gp_obj = None
    gp_data = None
    gp_layer = None
    gp_frame = None
    gp_drawing = None
    gp_material = None

    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.setup_gp()

    def clear(self):
        """Clear all strokes from the drawing"""
        if self.gp_drawing and self.gp_layer:
            # Remove all strokes
            self.gp_drawing.remove_strokes()
            
            # Update the view
            if bpy.context.view_layer:
                bpy.context.view_layer.update()

    def add_box(self, position, size=1.0):
        self.add_line([
            position + Vector((-0.5, -0.5, -0.5)) * size,
            position + Vector((+0.5, -0.5, -0.5)) * size,
            position + Vector((+0.5, +0.5, -0.5)) * size,
            position + Vector((-0.5, +0.5, -0.5)) * size,
            position + Vector((-0.5, -0.5, -0.5)) * size,
        ])
        self.add_line([
            position + Vector((-0.5, -0.5, -0.5)) * size,
            position + Vector((-0.5, -0.5, +0.5)) * size,
        ])
        self.add_line([
            position + Vector((+0.5, -0.5, -0.5)) * size,
            position + Vector((+0.5, -0.5, +0.5)) * size,
        ])
        self.add_line([
            position + Vector((+0.5, +0.5, -0.5)) * size,
            position + Vector((+0.5, +0.5, +0.5)) * size,
        ])
        self.add_line([
            position + Vector((-0.5, +0.5, -0.5)) * size,
            position + Vector((-0.5, +0.5, +0.5)) * size,
        ])
        self.add_line([
            position + Vector((-0.5, -0.5, +0.5)) * size,
            position + Vector((+0.5, -0.5, +0.5)) * size,
            position + Vector((+0.5, +0.5, +0.5)) * size,
            position + Vector((-0.5, +0.5, +0.5)) * size,
            position + Vector((-0.5, -0.5, +0.5)) * size,
        ])

    # def add_cross(self, position, size=1.0):
    # 	print("...")
    def add_circle(self, position, radius=1, sides=8, alpha=1.0, dash=0.0):

        for i in range(sides):
            a0 = ((i + 0) * (360 / sides)) * math.pi / 180
            a1 = ((i + 1) * (360 / sides)) * math.pi / 180
            A = position + Vector((math.cos(a0), math.sin(a0), 0)) * radius
            B = position + Vector((math.cos(a1), math.sin(a1), 0)) * radius
            self.add_line([A, B], alpha=alpha, dash=dash)

    def add_lines(self, lines, alpha=1.0, dash=0.0):
        for line in lines:
            self.add_line(line, alpha, dash)

    def add_line(self, points, alpha=1.0, dash=0.0):

        """Add a line (stroke) with given points"""
        if not self.gp_drawing:
            return
        
        if dash == 0:
            # Create a single stroke with all points
            self.gp_drawing.add_strokes(sizes=[len(points)])
            stroke = self.gp_drawing.strokes[-1]  # Get the last stroke
            
            # Set stroke properties
            stroke.material_index = 0
            
            # Set point positions and properties
            for i, point_co in enumerate(points):
                point = stroke.points[i]
                point.position = point_co
                point.opacity = alpha
                point.radius = 0.02  # Line width - thinner for better visibility
                point.vertex_color = (*self.color, 1.0)  # Set vertex color
        else:
            # Dashed line - create multiple small strokes
            for i in range(len(points) - 1):
                length = (points[i+1] - points[i]).magnitude
                steps = math.floor((length / dash) / 2)
                A = points[i]
                B = points[i + 1]

                for s in range(steps):
                    # Add a small stroke for each dash segment
                    self.gp_drawing.add_strokes(sizes=[2])
                    stroke = self.gp_drawing.strokes[-1]
                    stroke.material_index = 0
                    
                    # First point of dash
                    stroke.points[0].position = A + (B - A).normalized() * (s * (dash * 2))
                    stroke.points[0].opacity = alpha
                    stroke.points[0].radius = 0.05
                    stroke.points[0].vertex_color = (*self.color, 1.0)
                    
                    # Second point of dash
                    stroke.points[1].position = A + (B - A).normalized() * (s * (dash * 2) + dash)
                    stroke.points[1].opacity = alpha
                    stroke.points[1].radius = 0.05
                    stroke.points[1].vertex_color = (*self.color, 1.0)

    def add_text(self, text, pos=Vector((0, 0, 0)), size=1.0):
        # text = text.upper()
        size_xy = Vector((0.66, 1)) * size
        padding = size_xy.x / 2

        offset = 0

        def add_character(strokes):
            nonlocal offset

            for stroke in strokes:
                path = []
                for id in stroke:
                    x = (id % 3) * (size_xy.x / 2) + (offset * (size_xy.x * 1.5)) + padding
                    y = math.floor(id / 3) * size_xy.y / 2 + padding
                    path.append(pos + Vector((x, -size_xy.y - 2 * padding + y, 0)))

                self.add_line(path)

        # 6 -- 7 -- 8
        # |    |    |
        # 3 -- 4 -- 5
        # |    |    |
        # 0 -- 1 -- 2
        # |    |    |
        #-3 - -2 - -1
        chars = {
            'a': [[0, 3, 5, 1, 0], [5, 2]],
            'b': [[6, 0, 2, 5, 3]],
            'c': [[5, 3, 0, 2]],
            'd': [[8, 2, 0, 3, 5]],
            'e': [[5, 3, 0, 5], [0, 2]],
            'f': [[7, 3, 0], [3, 4]],
            'g': [[2, 5, 3, 0, 2, -2, -3]],
            'h': [[6, 0], [3, 5, 2]],
            'i': [[4, 1], [7, 8]],
            'j': [[4, 1, -3], [7, 8]],
            'k': [[6, 0], [3, 4], [3, 1]],
            'l': [[6, 3, 1]],
            'm': [[0, 3, 5, 2], [4, 1]],
            'n': [[0, 3, 2, 5]],
            'o': [[0, 3, 5, 2, 0]],
            'p': [[-3, 3, 5, 2, 0]],
            'q': [[-1, 5, 3, 0, 2]],
            'r': [[3, 0, 4, 5]],
            's': [[5, 4, 0, 2, -2, -3]],
            't': [[3, 5], [4, 1]],
            'u': [[3, 0, 2, 5]],
            'v': [[3, 1, 5]],
            'w': [[3, 0, 4, 1, 5]],
            'x': [[3, 2], [0, 5]],
            'y': [[3, 1], [5, -3]],
            'z': [[3, 5, 0, 2]],

            # Alphabet Uppercase
            'A': [[0, 3, 7, 5, 2], [3, 5]],
            'B': [[0, 6, 8, 4, 2, 0], [3, 4]],
            'C': [[2, 1, 3, 7, 8]],
            'D': [[0, 6, 7, 5, 1, 0]],
            'E': [[2, 0, 6, 8], [3, 4]],
            'F': [[0, 6, 8], [3, 4]],
            'G': [[4, 5, 2, 0, 3, 7, 8]],
            'H': [[0, 6], [3, 5], [2, 8]],
            'I': [[0, 2], [1, 7], [6, 8]],
            'J': [[6, 8, 5, 1, 0, 3]],
            'K': [[6, 0], [3, 4, 8], [4, 2]],
            'L': [[6, 0, 2]],
            'M': [[0, 6, 4, 8, 2]],
            'N': [[0, 6, 2, 8]],
            'O': [[1, 3, 7, 5, 1]],
            'P': [[0, 6, 7, 5, 3]],
            'Q': [[1, 3, 7, 5, 1], [4, 2]],
            'R': [[0, 6, 8, 4, 2], [3, 4]],
            'S': [[0, 1, 5, 3, 7, 8]],
            'T': [[6, 8], [7, 1]],
            'U': [[6, 0, 2, 8]],
            'V': [[6, 3, 1, 5, 8]],
            'W': [[6, 0, 4, 2, 8]],
            'X': [[6, 2], [0, 8]],
            'Y': [[6, 4, 8], [4, 1]],
            'Z': [[6, 8, 0, 2]],

            # Special
            ' ': [],
            '.': [[1, 2]],
            ',': [[1, -2]],
            '+': [[3, 5], [7, 1]],
            '-': [[3, 5]],
            '_': [[0, 2]],
            '|': [[1, 7]],
            '/': [[0, 8]],
            '\\': [[6, 2]],
            "'": [[7, 4]],
            '*': [[0, 8], [3, 5], [6, 2], [1, 7]],
            '%': [[6, 3], [8, 0], [5, 2]],
            '"': [[6, 4], [7, 5]],
            '~': [[3, 7, 4, 8]],
            '@': [[0, 6, 8, 2, 1, 4]],
            '$': [[0, 1, 5, 3, 7, 8], [7, 1]],
            '^': [[3, 7, 5]],
            ':': [[4, 5], [1, 2]],
            ';': [[4, 5], [1, -3]],
            # '&': [[2,3,6,7,4,3,0,5]],

            # Pairs
            '(': [[1, 3, 7]],
            ')': [[7, 5, 1]],
            '[': [[7, 6, 0, 1]],
            ']': [[7, 8, 2, 1]],
            '<': [[8, 3, 2]],
            '>': [[6, 5, 0]],

            # Numbers
            '0': [[6, 8, 2, 0, 6], [0, 8]],
            '1': [[0, 2], [1, 7, 6]],
            '2': [[6, 7, 5, 3, 0, 2]],
            '3': [[6, 8, 4, 2, 0]],
            '4': [[6, 3, 5], [8, 2]],
            '5': [[8, 6, 3, 5, 1, 0]],
            '6': [[8, 7, 3, 0, 2, 5, 3]],
            '7': [[3, 6, 8, 5, 1]],
            '8': [[6, 2, 0, 8, 6]],
            '9': [[5, 3, 6, 8, 5, 1, 0]],

            # Unknown
            '?': [[3, 6, 8, 5, 4, 1]]
        }
        for char in text:
            if char in chars:
                add_character(chars[char])
            else:
                # unknown character
                add_character(chars['?'])
            offset += 1

    def is_valid(self):
        """Check if the grease pencil system is still valid"""
        try:
            if not self.gp_obj:
                return False
            # Check if object still exists (accessing .name will raise error if deleted)
            _ = self.gp_obj.name
            if self.gp_obj.name not in bpy.data.objects:
                return False
            if not self.gp_layer:
                return False
            if not self.gp_frame:
                return False
            if not self.gp_drawing:
                return False
            return True
        except ReferenceError:
            # Object was deleted
            return False

    def setup_gp(self):
        """
        Set up Grease Pencil v3 object, layer, and frame
        This replaces the legacy annotations system
        """
        gp_name = f"BGE_Fence_{self.name}"
        
        # Check if we already have a GP object
        if gp_name in bpy.data.objects:
            self.gp_obj = bpy.data.objects[gp_name]
            self.gp_data = self.gp_obj.data
        else:
            # Create new Grease Pencil v3 data
            self.gp_data = bpy.data.grease_pencils_v3.new(gp_name)
            
            # Create object and link to scene
            self.gp_obj = bpy.data.objects.new(gp_name, self.gp_data)
            bpy.context.scene.collection.objects.link(self.gp_obj)
        
        # Create or get material
        mat_name = f"BGE_FenceMat_{self.name}"
        if mat_name in bpy.data.materials:
            self.gp_material = bpy.data.materials[mat_name]
        else:
            self.gp_material = bpy.data.materials.new(mat_name)
            
            # Use nodes for better color rendering
            self.gp_material.use_nodes = True
            nodes = self.gp_material.node_tree.nodes
            links = self.gp_material.node_tree.links
            
            # Clear default nodes
            nodes.clear()
            
            # Add Principled BSDF
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
            bsdf.inputs['Base Color'].default_value = (*self.color, 1.0)
            # Add slight emission to make color more visible
            bsdf.inputs['Emission Color'].default_value = (*self.color, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 0.3
            
            # Add Material Output
            output = nodes.new('ShaderNodeOutputMaterial')
            output.location = (200, 0)
            
            # Link
            links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Ensure material is in the GP object
        if self.gp_material.name not in self.gp_data.materials:
            self.gp_data.materials.append(self.gp_material)
        
        # Get or create layer
        layer_name = "BGE_Layer"
        if layer_name in self.gp_data.layers:
            self.gp_layer = self.gp_data.layers[layer_name]
        else:
            self.gp_layer = self.gp_data.layers.new(layer_name)
        
        # Get or create frame
        current_frame = bpy.context.scene.frame_current
        self.gp_frame = None
        
        # Check if frame exists at current frame number
        for frame in self.gp_layer.frames:
            if frame.frame_number == current_frame:
                self.gp_frame = frame
                break
        
        # Create frame if it doesn't exist
        if not self.gp_frame:
            self.gp_frame = self.gp_layer.frames.new(current_frame)
        
        # Get the drawing from the frame
        self.gp_drawing = self.gp_frame.drawing
        
        # Enable show in front (X-ray mode) so fences are visible through objects
        self.gp_obj.show_in_front = True
