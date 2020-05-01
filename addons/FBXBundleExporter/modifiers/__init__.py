print('--> RELOADED MODIFIERS')

from . import modifier_rename
from . import modifier_merge
from . import modifier_copy_modifiers
from . import modifier_collider
from . import modifier_LOD
from . import modifier_vertex_ao
from . import modifier_offset_transform

local_variables = locals().copy()
modifiers_dict = {}

for x in local_variables:
	if x.startswith('modifier_'):
		module=local_variables[x]
		modifiers_dict[module.Settings.id] = {
		'module':module,
		'global':module.Settings, 
		'local':''}

local_settings = []

from . import modifier

import bpy

modifier_annotations = {}
for x in modifiers_dict:
	SettingsGlobal = type(modifiers_dict[x]['global'].id+"SettingsAddon", (modifiers_dict[x]['global'],), modifiers_dict[x]['global'].__dict__.copy())
	modifier_annotations[modifiers_dict[x]['global'].settings_name()] = (bpy.props.PointerProperty, {'type': SettingsGlobal})
	modifiers_dict[x]['addon'] = SettingsGlobal
BGE_modifiers = type("BGE_modifiers", (bpy.types.PropertyGroup,), {'__annotations__': modifier_annotations})
BGE_modifiers_local = None

#creates a copy of the modifiers class but it changes the defaults to the ones in the addon preferences
def create_local_settings(Settings, defaults_path, name):
	new_annotattions = {}
	
	for key in Settings.__annotations__:
		preferences_val = eval("{}.{}".format(defaults_path, key))
		prop_data = Settings.__annotations__[key][1] #copy the original dictionary
		prop_data['default'] = preferences_val
		new_annotattions[key] = (Settings.__annotations__[key][0], prop_data)
		#new_annotattions[key]['default']=preferences_val
	SettingsScene = type(name+"Settings", (Settings,), {'__annotations__':new_annotattions})
	return SettingsScene

def register_globals():
	print('--> REGISTER_GLOBALS')
	global BGE_modifiers_global
	from bpy.utils import register_class
	modifier_annotations = {}
	for x in modifiers_dict:
		register_class(modifiers_dict[x]['addon'])


	BGE_modifiers_global = type("BGE_modifiers_global", (bpy.types.PropertyGroup,), {'__annotations__': modifier_annotations})
	register_class(BGE_modifiers)

def register_locals():
	print('--> REGISTER_LOCALS')
	global BGE_modifiers_local
	from bpy.utils import register_class
	modifier_annotations = {}
	for x in modifiers_dict:
		local_setting = create_local_settings(modifiers_dict[x]['global'], modifiers_dict[x]['global'].settings_path_global(), modifiers_dict[x]['global'].id)
		modifiers_dict[x]['local'] = local_setting
		register_class(local_setting)
		modifier_annotations[modifiers_dict[x]['global'].settings_name()] = (bpy.props.PointerProperty, {'type': local_setting})
	BGE_modifiers_local = type("BGE_modifiers_local", (bpy.types.PropertyGroup,), {'__annotations__': modifier_annotations})
	register_class(BGE_modifiers_local)

def unregister_globals():
	print('### UNREGISTER_GLOBALS')
	from bpy.utils import unregister_class

	unregister_class(BGE_modifiers)

	for x in modifiers_dict:
		unregister_class(modifiers_dict[x]['addon'])

def unregister_locals():
	print('### UNREGISTER_LOCALS')
	from bpy.utils import unregister_class

	unregister_class(BGE_modifiers_local)

	for x in modifiers_dict:
		unregister_class(modifiers_dict[x]['local'])

def draw(layout, context, modifier_group, types=('GENERAL','MESH')):
	col = layout.column()
	for x in modifiers_dict:
		modifier = getattr(modifier_group, modifiers_dict[x]['global'].settings_name())
		#if modifier.type in types:
		box = col.box()
		#box.label(text=str(modifier.global_settings))
		modifier.draw(box)