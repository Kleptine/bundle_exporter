import bpy
import os
import mathutils
import math

import pathlib

import traceback

from .. import modifiers
from .. import bundles

prefix_copy = "EXPORT_ORG_"


def _show_export_error(e):
    traceback.print_exc()
    error_msg = str(e)
    def draw_error(self, context):
        self.layout.label(text=error_msg)
    bpy.context.window_manager.popup_menu(draw_error, title="Export Failed", icon='ERROR')


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
            bundles.exporter.export(bundle_list)
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
            bundles.exporter.export(export_bundles)
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
            bundles.exporter.export([bundles.get_bundles()[bpy.context.scene.BGE_Settings.bundle_index]])
        except Exception as e:
            _show_export_error(e)
            return {'CANCELLED'}

        return {'FINISHED'}
