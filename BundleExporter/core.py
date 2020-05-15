import bpy
import os
import math
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

from . import gp_draw
from . import modifiers
from . import operators
from . import bundles
from . import settings
from .settings import mode_bundle_types, mode_pivot_types


def set_path(self, value):
    # checks if the provided path is inside a subdirectory of the current file to save it as a relative path
    if bpy.data.is_saved:
        value = os.path.realpath(bpy.path.abspath(value))
        file_path = os.path.dirname(os.path.realpath(bpy.path.abspath(bpy.data.filepath)))
        if os.path.commonprefix([os.path.realpath(bpy.path.abspath(value)), file_path]) == file_path:
            value = bpy.path.relpath(value)

    self.real_path = value


def get_path(self):
    return self.real_path


def get_preset_enum(self, context):
    prefs = context.preferences.addons[__name__.split('.')[0]].preferences
    presets = settings.get_presets(context.scene.BGE_Settings.export_format)
    if context.scene.BGE_Settings.export_format == prefs.export_format and prefs.export_preset in presets.keys():
        index = list(presets.keys()).index(prefs.export_preset)
        enum = settings.create_preset_enum(presets)
        enum[0], enum[index] = enum[index], enum[0]
        return enum
    else:
        enum = settings.create_preset_enum(presets)
        return enum

    return []


class BGE_Settings(bpy.types.PropertyGroup):
    real_path: bpy.props.StringProperty(default="")
    path: bpy.props.StringProperty(
        name="Output Path",
        default="",
        description="Define the path where to export or import from",
        subtype='DIR_PATH',
        get=get_path,
        set=set_path
    )
    padding: bpy.props.FloatProperty(
        name="Padding",
        default=0.15,
        min=0,
        description="Padding for fences",
        subtype='DISTANCE'
    )
    collapseBundles: bpy.props.BoolProperty(
        name="Collapse",
        default=False,
        description="Compact list view"
    )
    recent: bpy.props.StringProperty(
        name="Recent export",
        default=""
    )
    bundles: bpy.props.CollectionProperty(
        type=bundles.Bundle
    )
    bundle_index: bpy.props.IntProperty(
        name="Bundles",
        default=False,
        description="Bundles"
    )
    show_bundle_objects: bpy.props.BoolProperty(
        name="Show bundle objects",
        default=True,
    )

    mode_bundle: bpy.props.EnumProperty(items=mode_bundle_types, name="Bundle Mode", default=bpy.context.preferences.addons[__name__.split('.')[0]].preferences.mode_bundle)
    mode_pivot: bpy.props.EnumProperty(items=mode_pivot_types, name="Pivot From", default=bpy.context.preferences.addons[__name__.split('.')[0]].preferences.mode_pivot)

    scene_modifiers: bpy.props.PointerProperty(type=modifiers.BGE_modifiers_local)  # sometimes this variable may point to an old version, maybe force reload modules will fix it

    export_format: bpy.props.EnumProperty(items = settings.export_formats, default = bpy.context.preferences.addons[__name__.split('.')[0]].preferences.export_format)
    export_preset: bpy.props.EnumProperty(items = get_preset_enum)


class BGE_PT_core_panel(bpy.types.Panel):
    bl_idname = "BGE_PT_core_panel"
    bl_label = "Main Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bundle Exporter"

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        row = box.row(align=True)
        row.operator('bge.load_preferences', text='', icon='RECOVER_LAST')
        row.label(text='Settings', icon='PREFERENCES')

        col = box.column(align=True)

        row = col.row(align=True)
        if context.scene.BGE_Settings.path == "":
            row.alert = True
        row.prop(context.scene.BGE_Settings, "path", text="")
        if context.scene.BGE_Settings.path != "":
            row = row.row(align=True)
            row.operator("wm.path_open", text="", icon='FILE_TICK').filepath = context.scene.BGE_Settings.path

        row = col.row(align=True)
        row.prop(context.scene.BGE_Settings, "export_format", text='', icon = 'FILE_CACHE')
        row.prop(context.scene.BGE_Settings, "export_preset", text='', icon='PRESET')

        row = col.row(align=True)
        row.prop(context.scene.BGE_Settings, "mode_bundle", text="Bundle by")
        row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_bundle"

        row = col.row(align=True)
        row.prop(context.scene.BGE_Settings, "mode_pivot", text="Pivot at", icon='OUTLINER_DATA_EMPTY', expand=False)
        row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_pivot"

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene.BGE_Settings, "padding", text="Padding", expand=True)

        # Warnings
        col.alert = True
        if context.space_data.local_view:
            box = col.box()
            box.label(text="Can't export in local view mode.", icon='CANCEL')

        if context.active_object and context.active_object.mode != 'OBJECT':
            box = col.box()
            box.label(text="Requires object mode to export.", icon='CANCEL')

        if context.scene.BGE_Settings.path == "":
            box = col.box()
            box.label(text="No output path defined.", icon='CANCEL')

        elif context.scene.BGE_Settings.mode_bundle == 'COLLECTION' and len(bpy.data.collections) == 0:
            box = col.box()
            box.label(text="No groups available", icon='CANCEL')


class BGE_PT_modifiers_panel(bpy.types.Panel):
    bl_idname = "BGE_PT_modifiers_panel"
    bl_label = "Export Modifiers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bundle Exporter"
    bl_context = "objectmode"

    def draw(self, context):
        self.layout.operator_menu_enum(operators.BGE_OT_add_bundle_modifier.bl_idname, 'option')
        modifiers.draw(self.layout, context, bpy.context.scene.BGE_Settings.scene_modifiers, draw_only_active=True)


class BGE_UL_bundles(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        col = layout.column()
        row = col.row()
        icon = 'RESTRICT_SELECT_ON'
        if item.is_bundle_obj_selected():
            icon = 'RESTRICT_SELECT_OFF'
        row.operator(operators.op_bundles.BGE_OT_select.bl_idname, text='', icon=icon).index = index
        row.alert = not item.is_key_valid()
        row.label(text=item.filename, icon="FILE_3D")

        row.operator(operators.op_bundles.BGE_OT_remove.bl_idname, text='', icon='CANCEL').index = index

    def invoke(self, context, event):
        pass


class BGE_PT_files_panel(bpy.types.Panel):
    bl_idname = "BGE_PT_files_panel"
    bl_label = "Bundles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bundle Exporter"
    bl_context = "objectmode"
    # bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        # Get bundles
        bundle_list = bundles.get_bundles()
        selected_bundles = [x for x in bundle_list if x.is_bundle_obj_selected()]

        icon = 'EXPORT'

        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator(operators.BGE_OT_fence_draw.bl_idname, text="Draw Fences", icon='AXIS_TOP')
        row.operator(operators.BGE_OT_fence_clear.bl_idname, text="", icon='PANEL_CLOSE')

        col.template_list("BGE_UL_bundles", "", bpy.context.scene.BGE_Settings, "bundles", bpy.context.scene.BGE_Settings, "bundle_index", rows=2)

        row = col.row(align=True)

        split = row.split(factor=0.4, align=True)

        c = split.column(align=True)
        c.scale_y = 1.85
        c.operator(operators.BGE_OT_create_bundle.bl_idname, text="Create", icon='IMPORT')

        c = split.column(align=True)
        c.scale_y = 1.85
        c.operator(operators.BGE_OT_file_export_scene_selected.bl_idname, text="Export Selected ({}x)".format(len(selected_bundles)), icon=icon)

        col.operator(operators.BGE_OT_file_export.bl_idname, text="Export All ({}x)".format(len(bundles.get_bundles(only_valid=True))), icon=icon)

        bundle_index = bpy.context.scene.BGE_Settings.bundle_index

        if bpy.context.scene.BGE_Settings.bundle_index < len(bundle_list) and len(bundle_list) > 0:
            box = layout.box()
            box.label(text=bundle_list[bundle_index].filename, icon='FILE_3D')
            col = box.column()
            col.alert = not bundle_list[bundle_index].is_key_valid()
            col.prop(bundle_list[bundle_index], "key", text="", expand=True)

            split = col.split(factor=0.5, align=True)
            split.prop(bundle_list[bundle_index], "mode_bundle", text="", icon='GROUP')
            split.prop(bundle_list[bundle_index], "mode_pivot", text="", icon='OUTLINER_DATA_EMPTY')

            col.operator(operators.BGE_OT_file_export_selected.bl_idname, text="Export {}".format(bundle_list[bundle_index].filename), icon=icon)

            sub_box = box.box()
            row = sub_box.row(align=True)
            row.prop(
                bpy.context.scene.BGE_Settings,
                'show_bundle_objects',
                icon="TRIA_DOWN" if bpy.context.scene.BGE_Settings.show_bundle_objects else "TRIA_RIGHT",
                icon_only=True,
                text='Bundle objects:',
                emboss=False
            )
            if bpy.context.scene.BGE_Settings.show_bundle_objects:
                sub_box = sub_box.column(align=True)
                objs = bundle_list[bundle_index].objects
                for x in objs:
                    icon = 'OUTLINER_OB_MESH'
                    if x.type == 'ARMATURE':
                        icon = 'OUTLINER_OB_ARMATURE'
                    elif x.type == 'EMPTY':
                        icon = 'OUTLINER_OB_EMPTY'
                    sub_box.label(text=x.name, icon=icon)

            
            box.operator_menu_enum(operators.BGE_OT_override_bundle_modifier.bl_idname, 'option')
            modifiers.draw(box, context, bundle_list[bundle_index].override_modifiers, draw_only_active=True)

        layout.separator()


addon_keymaps = []
classes = [BGE_Settings, BGE_UL_bundles, BGE_PT_core_panel, BGE_PT_modifiers_panel, BGE_PT_files_panel]


def register():
    print('--> REGISTER_CORE')
    from bpy.utils import register_class
    register_class(bundles.Bundle)

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.BGE_Settings = bpy.props.PointerProperty(type=BGE_Settings)


def unregister():
    print('### UNREGISTER CORE')
    from bpy.utils import unregister_class
    unregister_class(bundles.Bundle)

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.BGE_Settings
