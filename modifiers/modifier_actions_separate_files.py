import os
import bpy
import pathlib

from . import modifier
from .. import settings


class BGE_mod_actions_separate_files(modifier.BGE_mod_default):
    label = "Export actions as files"
    id = 'actions_separate_files'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'ARMATURE'
    icon = 'FILE_MOVIE'
    priority = 99999
    tooltip = 'For each armature being exported, it will search for actions that are compatible with it and a separate FBX file will be exported for each armature and action combination. Useful for game development'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )

    path: bpy.props.StringProperty(default="{bundle_path}")
    file: bpy.props.StringProperty(default="{action_name}")

    def _warning(self):
        return bpy.context.scene.BGE_Settings.export_format != 'FBX'

    def _draw_info(self, layout):
        col = layout.column(align=True)
        col.prop(self, "path", text="Path")
        col.prop(self, "file", text="File")

    def process(self, bundle_info):
        if self._warning():
            return

        # from fbx addon exporter:
        def validate_actions(act, path_resolve):
            for fc in act.fcurves:
                data_path = fc.data_path
                if fc.array_index:
                    data_path = data_path + "[%d]" % fc.array_index
                try:
                    path_resolve(data_path)
                except ValueError:
                    return False
            return True

        export_preset = bundle_info['export_preset'].copy()

        export_preset['bake_anim'] = True
        export_preset['bake_anim_use_all_actions'] = False
        export_preset['bake_anim_use_nla_strips'] = False
        export_preset['use_selection'] = True

        for armature in bundle_info['armatures']:
            for act in bpy.data.actions:
                if validate_actions(act, armature.path_resolve):
                    bpy.context.scene.frame_start = act.frame_range[0]
                    bpy.context.scene.frame_end = act.frame_range[1]
                    folder = self.path.format(bundle_path=bundle_info['path'])
                    file = self.file.format(action_name=act.name)

                    path_full = os.path.join(bpy.path.abspath(folder), file) + "." + settings.export_format_extensions[bundle_info['export_format']]
                    directory = os.path.dirname(path_full)
                    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

                    export_preset['filepath'] = path_full

                    bpy.ops.object.select_all(action="DESELECT")
                    armature.select_set(True)
                    armature.animation_data.action = act
                    settings.export_operators[bundle_info['export_format']](**export_preset)

        # animations are already exported, there is no use in exporting them again for the main fbx file
        bundle_info['export_preset']['bake_anim'] = False
