import bpy

from . import platforms
from . import modifiers

from .__init__ import mode_bundle_types, mode_pivot_types


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
        if self.mode_bundle == 'NAME':#gets objects similar to the name of the key
            pass
        elif self.mode_bundle == 'PARENT': #gets the children of the obj of name 3key
            pass
        elif self.mode_bundle == 'COLLECTION':#gets objects under the collection named #key
            pass
        elif self.mode_bundle == 'SCENE':
            pass
        return []

    def is_key_valid(self):
        if self.mode_bundle == 'NAME':
            return self.key in bpy.context.scene.objects
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
        self._get_objects(types=('MESH','FONT','CURVE'))

    @property
    def helpers(self):
        self._get_objects(types=('EMPTY'))

    @property
    def armatures(self):
        self._get_objects(types=('ARMATURE'))

    @property
    def objects(self):
        return [0,1,2,3,4]
        return self.meshes + self.helpers +self.armatures

    @property
    def pivot(self):
        return (0,0,0)

    @property
    def filename(self):
        return platforms.platforms[bpy.context.scene.BGE_Settings.target_platform].get_filename(self.key)

    def select():
        print('SELECT BUNDLE ' + self.key)

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
    