import bpy
import os
import importlib

# ---------------------------------------------------------------------------- #
#                            AUTO LOAD ALL MODIFIERS                           #
# ---------------------------------------------------------------------------- #
# TODO: this should be cleaned out of unnecessary variables, the dictionary is probably not needed anymore
# ! no need to have a reference to the module

tree = [x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x.endswith('.py') and x != '__init__.py']

for i in tree:
    importlib.import_module('.' + i, package=__package__)

__globals = globals().copy()

modifiers_dict = {}

num_id = 1
for x in [x for x in __globals if x.startswith('modifier_')]:
    for y in [item for item in dir(__globals[x]) if item.startswith('BGE_mod_')]:
        mod = getattr(__globals[x], y)
        mod.unique_num = num_id
        num_id += 1
        modifiers_dict[mod.id] = {
            'module': __globals[x],
            'global': mod,
            'local': ''
        }

local_settings = []

# ---------------------------------------------------------------------------- #
#                              REGISTER/UNREGISTER                             #
# ---------------------------------------------------------------------------- #

# creates a property group with all modifiers
# BGE_modifiers is used by the addon preferences
# BGE_modifiers_local is used by the bundles and scenes and it references the addon preferences for its default values
modifier_annotations = {}
for x in modifiers_dict:
    SettingsGlobal = type(modifiers_dict[x]['global'].__name__, (modifiers_dict[x]['global'],), modifiers_dict[x]['global'].__dict__.copy())
    modifiers_dict[x]['addon'] = SettingsGlobal

    modifier_annotations[modifiers_dict[x]['global'].settings_name()] = (bpy.props.PointerProperty, {'type': modifiers_dict[x]['addon']})
BGE_modifiers = type("BGE_modifiers", (bpy.types.PropertyGroup,), {'__annotations__': modifier_annotations})
BGE_modifiers_local = None


# creates a copy of the modifiers class but it changes the defaults to the ones in the addon preferences
def create_local_settings(Settings, defaults_path, name):
    new_annotattions = {}

    for key in Settings.__annotations__:
        preferences_val = eval("{}.{}".format(defaults_path, key))
        prop_data = Settings.__annotations__[key][1]  # copy the original dictionary
        if not 'type' in prop_data:
            prop_data['default'] = preferences_val
        new_annotattions[key] = (Settings.__annotations__[key][0], prop_data)
        # new_annotattions[key]['default']=preferences_val
    SettingsScene = type(name, (Settings,), {'__annotations__': new_annotattions})
    return SettingsScene


# registers the modifiers referenced by the addon settings
def register_globals():
    print('--> REGISTER_GLOBALS')
    global BGE_modifiers_global
    from bpy.utils import register_class
    for x in modifiers_dict:
        modifiers_dict[x]['addon'].register_dependants()
        register_class(modifiers_dict[x]['addon'])
        
    register_class(BGE_modifiers)


# registers the modifiers used by the scene and bundles (they are registered after the addon preferences because they need to reference it)
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
        modifiers_dict[x]['addon'].unregister_dependants()


def unregister_locals():
    print('### UNREGISTER_LOCALS')
    from bpy.utils import unregister_class

    unregister_class(BGE_modifiers_local)

    for x in modifiers_dict:
        unregister_class(modifiers_dict[x]['local'])

# ---------------------------------------------------------------------------- #
#                                   UTILITIES                                  #
# ---------------------------------------------------------------------------- #


def get_modifiers_iter(modifier_group):
    for x in modifier_group.keys():
        if x.startswith('BGE_modifier_'):
            try:
                attr = getattr(modifier_group, x)
                yield attr
            except AttributeError:
                pass


def get_modifiers(modifier_group):
    return [x for x in get_modifiers_iter(modifier_group)]


def draw(layout, context, modifier_group, draw_only_active=False, types={'GENERAL', 'MESH', 'HELPER', 'ARMATURE'}):
    col = layout.column()

    modifiers_to_draw = []
    for x in modifiers_dict:
        modifier = getattr(modifier_group, modifiers_dict[x]['global'].settings_name())
        if modifier.type in types:
            if not draw_only_active or modifier.active:
                modifiers_to_draw.append(modifier)
    modifiers_to_draw = sorted(modifiers_to_draw)
    for x in modifiers_to_draw:
        box = col.box()
        x.draw(box, active_as_x=draw_only_active)
