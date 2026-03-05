import bpy
import os
import mathutils
import math

import pathlib

import traceback

from .. import modifiers
from .. import bundles
from .. import settings

def _show_export_error(e):
    traceback.print_exc()
    error_msg = str(e)
    def draw_error(self, context):
        self.layout.label(text=error_msg)
    bpy.context.window_manager.popup_menu(draw_error, title="Export Failed", icon='ERROR')


class BGE_OT_fix_contamination(bpy.types.Operator):
    """Remove stale custom properties left behind by a prior failed export"""
    bl_idname = "bge.fix_contamination"
    bl_label = "Cleanup Stale Export State"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Some objects have been left in a temporary state")
        col.label(text="due to a bug during export. You should check the file")
        col.label(text="to make sure it is as you expect.")

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Affected objects:")
        for obj in bpy.data.objects:
            if any(key in obj for key in settings.contamination_props_object):
                col.label(text="    " + obj.name, icon='OBJECT_DATA')

        for coll in bpy.data.collections:
            if any(key in coll for key in settings.contamination_props_collection):
                col.label(text="    " + coll.name, icon='OUTLINER_COLLECTION')

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Press OK to accept the current state of the file")
        col.label(text="as correct and remove stale properties, or Cancel to abort.")

    def execute(self, context):
        removed = 0

        for obj in bpy.data.objects:
            for key in list(obj.keys()):
                if key in settings.contamination_props_object:
                    del obj[key]
                    removed += 1

        for coll in bpy.data.collections:
            for key in list(coll.keys()):
                if key in settings.contamination_props_collection:
                    del coll[key]
                    removed += 1

        self.report({'INFO'}, "Removed {} stale export properties".format(removed))
        return {'FINISHED'}


class BGE_OT_file_export(bpy.types.Operator):
    bl_idname = "bge.file_export"
    bl_label = "export"
    bl_description = "Export All Bundles"

    @classmethod
    def poll(cls, context):
        if context.space_data.local_view:
            return False

        if bpy.context.scene.BGE_Settings.path == "":
            return False

        if len(bundles.get_bundles(only_valid=True)) == 0:
            return False

        return True

    @classmethod
    def description(cls, context, properties):
        if context.space_data.local_view:
            return "Can't export in local view"

        if bpy.context.scene.BGE_Settings.path == "":
            return "Can't export if the export path is not set"

        if len(bundles.get_bundles(only_valid=True)) == 0:
            return "No bundles to export"

        return "Export All Bundles"

    def execute(self, context):
        # Warnings
        if bpy.context.scene.BGE_Settings.path == "":
            self.report({'ERROR_INVALID_INPUT'}, "Export path not set")
            return {'CANCELLED'}

        try:
            bundle_list = bundles.get_bundles(only_valid=True)
            bundles.export.export(bundle_list)
        except Exception as e:
            _show_export_error(e)
            return {'CANCELLED'}

        return {'FINISHED'}


class BGE_OT_file_export_scene_selected(bpy.types.Operator):
    bl_idname = "bge.file_export_scene_selected"
    bl_label = "export selected"
    bl_description = "Export Selected Bundles"

    @classmethod
    def poll(cls, context):
        if context.space_data.local_view:
            return False

        if bpy.context.scene.BGE_Settings.path == "":
            return False

        if len(bpy.context.scene.BGE_Settings.bundles) == 0:
            return False

        if len([x for x in bundles.get_bundles() if x.is_bundle_obj_selected()]) == 0:
            return False

        return True

    @classmethod
    def description(cls, context, properties):
        if context.space_data.local_view:
            return "Can't export in local view"

        if bpy.context.scene.BGE_Settings.path == "":
            return "Can't export if the export path is not set"

        if len(bpy.context.scene.BGE_Settings.bundles) == 0:
            return "No bundles to export"

        if len([x for x in bundles.get_bundles() if x.is_bundle_obj_selected()]) == 0:
            return "No bundle selected"

        return "Export selected bundles"

    def execute(self, context):
        try:
            export_bundles = [x for x in bundles.get_bundles() if x.is_bundle_obj_selected()]
            bundles.export.export(export_bundles)
        except Exception as e:
            _show_export_error(e)
            return {'CANCELLED'}

        return {'FINISHED'}


class BGE_OT_file_export_selected(bpy.types.Operator):
    bl_idname = "bge.file_export_selected"
    bl_label = "export selected"
    bl_description = "Export Selected Bundles"

    @classmethod
    def poll(cls, context):
        if context.space_data.local_view:
            return False

        if bpy.context.scene.BGE_Settings.path == "":
            return False

        if len(bpy.context.scene.BGE_Settings.bundles) == 0:
            return False

        if not(bpy.context.scene.BGE_Settings.bundle_index < len(bundles.get_bundles()) and len(bundles.get_bundles()) > 0):
            return False

        return True

    @classmethod
    def description(cls, context, properties):
        if context.space_data.local_view:
            return "Can't export in local view"

        if bpy.context.scene.BGE_Settings.path == "":
            return "Can't export if the export path is not set"

        if len(bpy.context.scene.BGE_Settings.bundles) == 0:
            return "No bundles to export"

        if not(bpy.context.scene.BGE_Settings.bundle_index < len(bundles.get_bundles()) and len(bundles.get_bundles()) > 0):
            return "No bundle selected"

        return "Export {}".format(bundles.get_bundles()[bpy.context.scene.BGE_Settings.bundle_index].filename)

    def execute(self, context):
        try:
            bundles.export.export([bundles.get_bundles()[bpy.context.scene.BGE_Settings.bundle_index]])
        except Exception as e:
            _show_export_error(e)
            return {'CANCELLED'}

        return {'FINISHED'}
