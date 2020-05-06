import bpy
import os
import mathutils
import math

import pathlib

from .. import modifiers
from .. import bundles

prefix_copy = "EXPORT_ORG_"


class BGE_OT_file_export(bpy.types.Operator):
    bl_idname = "bge.file_export"
    bl_label = "export"
    bl_description = "Export Bundles"

    @classmethod
    def poll(cls, context):
        if context.space_data.local_view:
            return False

        if bpy.context.scene.BGE_Settings.path == "":
            return False

        if len(bundles.get_bundles(only_valid=True)) == 0:
            return False

        return True

    def execute(self, context):
        # Warnings
        if bpy.context.scene.BGE_Settings.path == "":
            self.report({'ERROR_INVALID_INPUT'}, "Export path not set" )
            return

        folder = bpy.path.abspath(bpy.context.scene.BGE_Settings.path)
        if not os.path.exists(folder):
            self.report({'ERROR_INVALID_INPUT'}, "Path doesn't exist" )
            return

        bundle_list = bundles.get_bundles(only_valid=True)
        bundles.exporter.export(bundle_list,  bpy.context.scene.BGE_Settings.path, bpy.context.scene.BGE_Settings.export_format, bpy.context.scene.BGE_Settings.export_preset)

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

    def execute(self, context):
        bundles.exporter.export((x for x in bundles.get_bundles() if x.is_bundle_obj_selected()), bpy.context.scene.BGE_Settings.path, bpy.context.scene.BGE_Settings.export_format, bpy.context.scene.BGE_Settings.export_preset)

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

    def execute(self, context):
        bundles.exporter.export([bundles.get_bundles()[bpy.context.scene.BGE_Settings.bundle_index]],  bpy.context.scene.BGE_Settings.path, bpy.context.scene.BGE_Settings.export_format, bpy.context.scene.BGE_Settings.export_preset)

        return {'FINISHED'}
