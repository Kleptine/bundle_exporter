import bpy
import bpy.utils.previews

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)

from . import operators
from . import modifiers
from . import settings
from .settings import mode_bundle_types, mode_pivot_types


bl_info = {
    "name": "Bundle Exporter",
    "description": "Export objects in bundles",
    "author": "AquaticNightmare",
    "blender": (2, 82, 0),
    "version": (2, 0, 1),
    "category": "3D View",
    "location": "3D View > Tools Panel > Bundle Exporter",
    "warning": "",
    "wiki_url": "https://gitlab.com/AquaticNightmare/bundle_exporter",
    "doc_url": "https://gitlab.com/AquaticNightmare/bundle_exporter",
    "tracker_url": "https://gitlab.com/AquaticNightmare/bundle_exporter/-/issues",
}


# https://blender.stackexchange.com/questions/118118/blender-2-8-field-property-declaration-and-dynamic-class-creation
def export_presets_getter(self, context):
    items = settings.get_presets_enum(bpy.context.preferences.addons[__name__.split('.')[0]].preferences.export_format)
    return items


def update_scene_export_preset(self, context):
    context.scene.BGE_Settings.export_preset = self.export_preset


class BGE_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    mode_bundle: bpy.props.EnumProperty(items=mode_bundle_types, name="Bundle Mode", default='COLLECTION')
    mode_pivot: bpy.props.EnumProperty(items=mode_pivot_types, name="Pivot From", default='OBJECT_FIRST')

    modifier_preferences: bpy.props.PointerProperty(type=modifiers.BGE_modifiers)

    export_format: bpy.props.EnumProperty(items=settings.export_formats)
    export_preset: bpy.props.EnumProperty(items=export_presets_getter, update=update_scene_export_preset)

    show_help: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        row.label(text='Default Settings (manually save preferences after changing values please)', icon='PREFERENCES')

        col = box.column(align=True)
        col.prop(self, 'export_format', text="Export Format")
        col.prop(self, 'export_preset', text="Export Preset")
        col.prop(self, "mode_bundle", text="Bundle by")
        col.prop(self, "mode_pivot", text="Bundle by", icon='OUTLINER_DATA_EMPTY')
        col.prop(self, "show_help", text="Show Help?", icon="INFO")

        modifiers.draw(col, context, self.modifier_preferences)

        col.operator('bge.save_preferences', text='Save User Preferences', icon='FILE_TICK')


def register():
    print('--> REGISTER INIT')
    from bpy.utils import register_class

    modifiers.register_globals()

    register_class(BGE_preferences)

    operators.register()

    modifiers.register_locals()

    from . import core
    import imp
    # to make sure it uses the correct variables when registering modifiers, otherwise errors will happen during development
    imp.reload(core)
    core.register()


def unregister():
    print('### UNREGISTER INIT')
    from bpy.utils import unregister_class

    from . import core
    core.unregister()

    modifiers.unregister_locals()

    operators.unregister()

    unregister_class(BGE_preferences)

    modifiers.unregister_globals()
