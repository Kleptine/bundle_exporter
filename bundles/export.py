import os
import pathlib
import time
import datetime

import bpy
from .. import settings

from .exporter import Exporter


def _is_relative_path(path):
    """Check if a path is relative (not absolute and not empty)."""
    if not path:
        return False
    # Blender's '//' prefix denotes blend-file-relative paths
    if path.startswith('//'):
        return True
    # Standard relative paths like '../' or 'subdir/'
    if not os.path.isabs(path):
        return True
    return False


def export(bundles):
    start_time = time.time()

    # Relative paths (like '../' or '//') resolve from the blend file's directory.
    # Without a saved file, there's no directory to resolve from.
    export_path = bpy.context.scene.BGE_Settings.path
    if _is_relative_path(export_path) and not bpy.data.is_saved:
        raise RuntimeError(
            f"Relative export path [{export_path}] requires the blend file to be saved first. Save the file or use an absolute path."
        )

    previous_selection = bpy.context.selected_objects.copy()
    previous_active = bpy.context.view_layer.objects.active
    previous_unit_system = bpy.context.scene.unit_settings.system
    previous_pivot = bpy.context.scene.tool_settings.transform_pivot_point
    previous_cursor = bpy.context.scene.cursor.location

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    if bpy.context.view_layer.objects.active:
        bpy.context.view_layer.objects.active = None

    # bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

    processed_bundles = 0

    for bundle in bundles:
        processed_bundles += 1
        with Exporter(bundle, bpy.context.scene.BGE_Settings.path, bpy.context.scene.BGE_Settings.export_format, bpy.context.scene.BGE_Settings.export_preset) as bundle_info:
            all_objects = bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']
            print('Copied objects to export: {}'.format(all_objects))

            #assert False
            bpy.ops.object.select_all(action="DESELECT")
            for modifier in bundle.modifiers:
                print('Pre-processing modifier "{}" ...'.format(modifier.id))
                modifier.pre_process(bundle_info)

            for modifier in bundle.modifiers:
                print('Appliying modifier "{}" ...'.format(modifier.id))
                modifier.process(bundle_info)
            # apply the pivot
            all_objects = bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']

            print('objects after modifiers: {}'.format(all_objects))

            for x in all_objects:
                if x.parent and x.parent in all_objects:
                    continue
                x.location -= bundle_info['pivot']

            # Resolve the export path to an absolute path.
            #
            # Path resolution requires the blend file to be saved when using relative paths,
            # because we need a known location on disk to resolve paths like '../' from.
            # The validation at the start of export() ensures this precondition is met.
            #
            # bpy.path.abspath() handles Blender's '//' prefix (blend-file-relative notation),
            # but standard relative paths like '../' need additional handling - we resolve
            # them relative to the blend file's parent directory.
            export_path = bundle_info['path']
            blend_dir = os.path.dirname(bpy.data.filepath)
            # First expand '//' prefix if present
            export_path = bpy.path.abspath(export_path)
            # If still relative (e.g. '../subfolder'), resolve from the blend file's directory
            if not os.path.isabs(export_path):
                export_path = os.path.normpath(os.path.join(blend_dir, export_path))

            path_full = os.path.join(export_path, bundle_info['name']) + "." + settings.export_format_extensions[bundle_info['export_format']]
            directory = os.path.dirname(path_full)
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

            # Select all export objects
            bpy.context.view_layer.objects.active = None
            bpy.ops.object.select_all(action="DESELECT")
            for obj in bundle_info['meshes'] + bundle_info['empties'] + bundle_info['armatures'] + bundle_info['extras']:
                obj.select_set(True)

            bundle_info['export_preset']['filepath'] = path_full
            operator = settings.export_operators[bundle_info['export_format']]
            valid_props = operator.get_rna_type().properties.keys()

            if 'use_selection' in valid_props:
                bundle_info['export_preset']['use_selection'] = True
            elif 'export_selected_objects' in valid_props:
                bundle_info['export_preset']['export_selected_objects'] = True

            settings.export_operators[bundle_info['export_format']](**bundle_info['export_preset'])

    # TODO: add this final part into a except/finally scope ?
    # Restore previous settings
    bpy.context.scene.unit_settings.system = previous_unit_system
    bpy.context.scene.tool_settings.transform_pivot_point = previous_pivot
    bpy.context.scene.cursor.location = previous_cursor
    bpy.context.view_layer.objects.active = previous_active
    bpy.ops.object.select_all(action='DESELECT')
    for obj in previous_selection:
        obj.select_set(True)

    # Show popup
    def draw(self, context):
        self.layout.operator("wm.path_open", text=bpy.context.scene.BGE_Settings.path, icon='FILE_FOLDER').filepath = bpy.context.scene.BGE_Settings.path

    bpy.context.window_manager.popup_menu(draw, title=f"Exported {processed_bundles}x bundles", icon='INFO')

    print("Exported in {} seconds".format(str(datetime.timedelta(seconds=(time.time() - start_time)))))
