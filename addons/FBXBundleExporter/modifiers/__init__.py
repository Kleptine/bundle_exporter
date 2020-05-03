print('--> RELOADED MODIFIERS')

# ---------------------------------------------------------------------------- #
#                            AUTO LOAD ALL MODIFIERS                           #
# ---------------------------------------------------------------------------- #

import os
import importlib
tree = [x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x.endswith('.py') and x != '__init__.py']

for i in tree:
	importlib.import_module('.'+i, package=__package__)

__globals = globals().copy()

modifiers_dict = {}

num_id = 1
for x in [x for x in __globals if x.startswith('modifier_')]:
	for y in [item for item in dir(__globals[x]) if item.startswith('BGE_')]:
		mod = getattr(__globals[x], y)
		mod.unique_num = num_id
		num_id +=1
		modifiers_dict[mod.id] = {
		'module':__globals[x],
		'global':mod, 
		'local':''}

local_settings = []

# ---------------------------------------------------------------------------- #
#                              REGISTER/UNREGISTER                             #
# ---------------------------------------------------------------------------- #

import bpy
modifier_annotations = {}
for x in modifiers_dict:
	SettingsGlobal = type(modifiers_dict[x]['global'].__name__, (modifiers_dict[x]['global'],), modifiers_dict[x]['global'].__dict__.copy())
	modifiers_dict[x]['addon'] = SettingsGlobal
	print(modifiers_dict[x]['addon'])

	modifier_annotations[modifiers_dict[x]['global'].settings_name()] = (bpy.props.PointerProperty, {'type': modifiers_dict[x]['addon']})
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
	SettingsScene = type(name, (Settings,), {'__annotations__':new_annotattions})
	return SettingsScene

def register_globals():
	print('--> REGISTER_GLOBALS')
	global BGE_modifiers_global
	from bpy.utils import register_class
	for x in modifiers_dict:
		register_class(modifiers_dict[x]['addon'])

	register_class(BGE_modifiers)

def register_locals():
	print('--> REGISTER_LOCALS')
	global BGE_modifiers_local
	from bpy.utils import register_class
	modifier_annotations = {}
	for x in modifiers_dict:
		local_setting = create_local_settings(modifiers_dict[x]['global'], modifiers_dict[x]['global'].settings_path_global(), modifiers_dict[x]['global'].__name__)
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

# ---------------------------------------------------------------------------- #
#                                   UTILITIES                                  #
# ---------------------------------------------------------------------------- #

def get_modifiers(modifier_group):
	return [getattr(modifier_group, x) for x in modifier_group.keys() if x.startswith('BGE_modifier_')]

def draw(layout, context, modifier_group, draw_only_active=False, types={'GENERAL','MESH', 'HELPER', 'ARMATURE'}):
	col = layout.column()
	for x in modifiers_dict:
		modifier = getattr(modifier_group, modifiers_dict[x]['global'].settings_name())
		if modifier.type in types:
			if not draw_only_active or modifier.active:
				box = col.box()
			#box.label(text=str(modifier.global_settings))
				modifier.draw(box)