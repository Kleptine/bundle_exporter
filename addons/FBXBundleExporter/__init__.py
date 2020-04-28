from . import operators
from . import modifiers
from . import icons

import bpy, bmesh
import bpy.utils.previews


bl_info = {
	"name": "Game Exporter",
	"description": "Export objects in bundles",
	"author": "renderhjs",
	"blender": (2, 80, 0),
	"version": (2, 0, 0),
	"category": "3D View",
	"location": "3D View > Tools Panel > Game Exporter",
	"warning": "",
	"wiki_url": "http://renderhjs.net/fbxbundle/",
	"tracker_url": "",
}

from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)

mode_bundle_types = [('NAME', 'Name', "Bundle by matching object names"), 
		('PARENT', 'Parent', "Bundle by the parent object"), 
		# ('SPACE', 'Space', "Bundle by shared space"), 
		('COLLECTION', 'Collection', "Bundle by 'Collections'"),
		('MATERIAL', 'Material', "Bundle by matching material names"),
		('SCENE', 'Scene', "Bundle by current scene")]
mode_pivot_types = [('OBJECT_FIRST', 'First Name', "Pivot at the first object sorted by name"), 
		('OBJECT_LOWEST', 'Lowest Object', "Pivot at the lowest Z object's pivot"),
		('BOUNDS_BOTTOM', 'Bottom Center', "Pivot at the bottom center of the bounds of the bundle"), 
		('SCENE', 'Scene 0,0,0', "Pivot at the Scene center 0,0,0'"),
		('PARENT', 'Parent', "Pivot from the parent object"),
		('EMPTY', 'Empty Gizmo', "Empty gizmo object of: Arrow, Plain Axes, Single Arrow>; global for all bundles (must be selected)"),
		('EMPTY_LOCAL', 'Empty Local Gizmo', "You need to have an empty of type Arrow, Plain Axes or Single Arrow located inside the bundle and its name needs to start with 'pivot'; for example 'pivot.001'")]
target_platform_types = [('UNITY', 'Unity ', 'Unity engine export, fixes axis rotation issues'),
		('UNREAL', 'Unreal ', 'Unreal engine export'),
		('BLENDER', 'Collada', 'Default Blender *.DAE export'),
		('GLTF', 'glTF', 'GL Transmission Format')]

#https://blender.stackexchange.com/questions/118118/blender-2-8-field-property-declaration-and-dynamic-class-creation
modifier_annotations = {}
for x in modifiers.modifiers_dict:
	modifier_annotations[modifiers.modifiers_dict[x]['modifier'].settings_name()] = (bpy.props.PointerProperty, {'type': modifiers.modifiers_dict[x]['global']})

BGE_preferences_modifiers = type("BGE_preferences_modifiers", (object,), {'__annotations__': modifier_annotations})

class BGE_preferences(bpy.types.AddonPreferences, BGE_preferences_modifiers):
	bl_idname = __name__

	mode_bundle: bpy.props.EnumProperty(items= mode_bundle_types, name = "Bundle Mode", default = 'NAME')
	mode_pivot: bpy.props.EnumProperty(items=mode_pivot_types, name = "Pivot From", default = 'OBJECT_FIRST')
	target_platform: bpy.props.EnumProperty(items= target_platform_types, description="Target platform for the FBX exports.",name = "Target Platform", default = 'UNITY')

	#BGE_modifier_collider: bpy.props.PointerProperty(type=modifiers.modifier_collider.Settings)
	

	def draw(self, context):
		layout = self.layout

		box = layout.box()
		row = box.row(align=True)
		row.label(text='Default Settings (manually save preferences after changing values please)', icon='PREFERENCES')

		icon = icons.icon_get(self.target_platform.lower())
		row.prop(self, "target_platform", text="", icon_value=icon)
		
		col = box.column(align=True)
		col.prop(self, "mode_bundle", text="Bundle by", icon='GROUP')
		col.prop(self, "mode_pivot", text="Bundle by", icon='OUTLINER_DATA_EMPTY')

		modifiers.draw(col, context, use_global_settings=True)

		col.operator('bge.save_preferences', text='Save User Preferences' ,icon = 'FILE_TICK')

		box = layout.box()
		row = box.row()
		row.label(text="Unity Editor script")
		row.operator(operators.BGE_OT_unity_script.bl_idname, icon='FILE_TICK')
		col = box.column(align=True)
		col.label(text="Copies a Unity Editor script to automatically assign")
		col.label(text="existing materials by name matching names in Blender")

		box = layout.box()
		row = box.row()
		row.label(text="Keyboard shortcuts")
		col = box.column(align=True)
		col.label(text="Ctrl + E = Export selected")
		col.label(text="Ctrl + Shift + E = Export recent")



addon_keymaps = []

def register():

	icons.register()

	modifiers.register_globals()

	from bpy.utils import register_class
	register_class(BGE_preferences)

	for operator in operators.operators:
		print("register operator: {}".format(operator))
		register_class(operator)

	from . import core
	core.register()


def unregister():
	from bpy.utils import unregister_class
	from . import core
	core.unregister()

	for operator in operators.operators:
		unregister_class(operator)

	try:
		unregister_class(BGE_preferences)
	except:
		print(BGE_preferences)

	modifiers.unregister_globals()

	icons.unregister()
