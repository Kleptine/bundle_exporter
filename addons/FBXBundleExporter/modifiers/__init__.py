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
		modifiers_dict[module.Modifier.id] = {
		'module':module, 
		'modifier':module.Modifier(), 
		'modifier_global':module.Modifier(use_global_settings=True), 
		'global':module.Settings, 
		'local':''}

local_settings = []

import bpy

def create_local_settings(Settings, defaults_path, name):
	new_annotattions = {}
	
	for key in Settings.__annotations__:
		preferences_val = eval("{}.{}".format(defaults_path, key))
		prop_data = Settings.__annotations__[key][1] #copy the original dictionary
		prop_data['default'] = preferences_val
		new_annotattions[key] = (Settings.__annotations__[key][0], prop_data)
		#new_annotattions[key]['default']=preferences_val
	SettingsScene = type(name+"Settings", (bpy.types.PropertyGroup,), {'__annotations__':new_annotattions})
	return SettingsScene

def register_globals():
	from bpy.utils import register_class
	for x in modifiers_dict:
		register_class(modifiers_dict[x]['global'])

def register_locals():
	from bpy.utils import register_class
	for x in modifiers_dict:
		local_setting = create_local_settings(modifiers_dict[x]['global'], modifiers_dict[x]['modifier'].settings_path_global(), modifiers_dict[x]['modifier'].id)
		modifiers_dict[x]['local'] = local_setting
		register_class(local_setting)
		setattr(bpy.types.Scene, modifiers_dict[x]['modifier'].settings_name(), bpy.props.PointerProperty(type=local_setting))

def unregister_globals():
	from bpy.utils import unregister_class
	for x in modifiers_dict:
		unregister_class(modifiers_dict[x]['global'])

def unregister_locals():
	from bpy.utils import unregister_class
	for x in modifiers_dict:
		unregister_class(modifiers_dict[x]['local'])
		delattr(bpy.types.Scene, modifiers_dict[x]['modifier'].settings_name())

def draw(layout, context, use_global_settings = False, types=('GENERAL','MESH')):
	col = layout.column()

	for modifier_id in modifiers_dict:
		modifier = modifiers_dict[modifier_id]['modifier_global'] if use_global_settings else modifiers_dict[modifier_id]['modifier']
		if modifier.type in types:
			box = col.box()
			modifier.draw(box)