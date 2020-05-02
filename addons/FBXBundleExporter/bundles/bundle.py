import operator

import bpy
from mathutils import Vector

from .. import platforms
from .. import modifiers


from ..__init__ import mode_bundle_types, mode_pivot_types


def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

class Bundle(bpy.types.PropertyGroup):

    key: bpy.props.StringProperty (
        default=''
    )

    mode_bundle: bpy.props.EnumProperty(items= mode_bundle_types, name = "Bundle Mode", default = 'NAME')
    mode_pivot: bpy.props.EnumProperty(items=mode_pivot_types, name = "Pivot From", default = 'OBJECT_FIRST')
    override_modifiers: bpy.props.PointerProperty(type=modifiers.BGE_modifiers)

    #https://stackoverflow.com/questions/3942303/how-does-a-python-set-check-if-two-objects-are-equal-what-methods-does-an-o
    def __hash__(self):
        return hash(self.key)
        
    def __eq__(self, other):
        return isinstance(other.__class__, Bundle) and self.key == other.key

    def _get_objects(self, types=()):
        if not self.is_key_valid():
            return []

        objs = set()
        if self.mode_bundle == 'NAME':#gets objects similar to the name of the key
            objs.update(x for x in bpy.context.scene.objects if x.name == self.key or (len(x.name)>= 4 and x.name[:-4]==self.key and x.name[-4] == '.' and x.name[-3:].isdigit()))

        elif self.mode_bundle == 'PARENT': #gets the children of the obj of name 3key
            obj = bpy.context.scene.objects[self.key]
            #objs.add(obj)
            objs.update(x for x in traverse_tree(obj))

        elif self.mode_bundle == 'COLLECTION':#gets objects under the collection named #key
            collection = next(x for x in bpy.data.collections if self.key == x.name)
            for coll in traverse_tree(collection):
                for obj in coll.objects:
                    objs.add(obj)
        elif self.mode_bundle == 'SCENE':
            objs.update(x for x in bpy.context.scene.objects)

        #filter types
        ans = [x for x in objs if x.type in types]
        return ans

    def is_key_valid(self):
        if self.mode_bundle == 'NAME':
            return(any(x.name == self.key or (len(x.name)>= 4 and x.name[:-4]==self.key and x.name[-4] == '.' and x.name[-3:].isdigit()) for x in bpy.context.scene.objects))
        elif self.mode_bundle == 'PARENT':
            return self.key in bpy.context.scene.objects
        elif self.mode_bundle == 'COLLECTION':
            return any([x.name == self.key for x in traverse_tree(bpy.context.scene.collection)])
        elif self.mode_bundle == 'SCENE':
            return True
        return False

    @property
    def target_platform(self):
        return bpy.context.scene.BGE_Settings.target_platform

    @property
    def meshes(self):
        return self._get_objects(types={'MESH','FONT','CURVE'})

    @property
    def helpers(self):
        return self._get_objects(types={'EMPTY'})

    @property
    def armatures(self):
        return self._get_objects(types={'ARMATURE'})

    @property
    def objects(self):
        return self._get_objects(types={'MESH','FONT','CURVE','EMPTY','ARMATURE'})

    @property
    def pivot(self):
        mode_pivot = self.mode_pivot
        objects = self.meshes
        

        if len(objects):
            if mode_pivot == 'OBJECT_FIRST':
                if len(objects) > 0:
                    return objects[0].location

            elif mode_pivot == 'BOUNDS_BOTTOM':
                bounds = ObjectBounds(objects[0])
                if len(objects) > 1:
                    for i in range(1,len(objects)):
                        bounds.combine( ObjectBounds(objects[i]) )

                return Vector((
                    bounds.min.x + bounds.size.x/2,
                    bounds.min.y + bounds.size.y/2,
                    bounds.min.z
                ))
            elif mode_pivot == 'OBJECT_LOWEST':

                obj_bounds = {}
                for obj in objects:
                    b = ObjectBounds(obj)
                    obj_bounds[obj] = b.min.z

                # Sort
                ordered = sorted(obj_bounds.items(), key=operator.itemgetter(1))
                return ordered[0][0].location


            elif mode_pivot == 'SCENE':
                return Vector((0,0,0))
            
            elif mode_pivot == 'PARENT':
                if len(objects) > 0:
                    if objects[0].parent:
                        return objects[0].parent.location
                    else:
                        return objects[0].location

            elif mode_pivot == 'EMPTY':
                for obj in self.helpers:
                    if obj.empty_display_type == 'SINGLE_ARROW' or obj.empty_display_type == 'PLAIN_AXES' or obj.empty_display_type == 'ARROWS':
                        return obj.location

            elif mode_pivot == 'EMPTY_LOCAL':
                for obj in self.helpers:
                    if obj.empty_display_type == 'SINGLE_ARROW' or obj.empty_display_type == 'PLAIN_AXES' or obj.empty_display_type == 'ARROWS':
                        if obj.name.lower().startswith('pivot'):
                            return obj.location

        # Default
        return Vector((0,0,0))

    @property
    def modifiers(self):
        scene_mods = modifiers.get_modifiers(bpy.context.scene.BGE_Settings.scene_modifiers)
        override_mods = modifiers.get_modifiers(self.override_modifiers)

        mods = {}
        num_scene_mods=0
        for x in scene_mods:
            if x.active:
                mods[x.id] = x
                num_scene_mods+=1
        for x in override_mods:
            if x.active:
                if x.id in mods:
                    num_scene_mods-=1
                mods[x.id] = x

        return sorted(mods.values())


    @property
    def filename(self):
        return platforms.platforms[bpy.context.scene.BGE_Settings.target_platform].get_filename(self.key)

    def select(self):
        bpy.ops.object.select_all(action='DESELECT')
        for x in self.objects:
            x.select_set(True)


    
class ObjectBounds:
	obj = None
	min = Vector((0,0,0))
	max = Vector((0,0,0))
	size = Vector((0,0,0))
	center = Vector((0,0,0))

	def __init__(self, obj):
		self.obj = obj
		corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

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