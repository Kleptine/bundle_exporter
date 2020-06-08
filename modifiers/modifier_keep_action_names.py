import bpy
import bmesh
import imp

from . import modifier


class BGE_mod_keep_action_names(modifier.BGE_mod_default):
    label = "Keep Action Names"
    id = 'keep_action_names'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'ARMATURE'
    icon = 'ACTION_TWEAK'
    priority = 0
    tooltip = 'Modifies the FBX exporter to keep action names (it will break the export if you are exporting multiple objects that share the same action)'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )

    def _warning(self):
        return bpy.context.scene.BGE_Settings.export_format != 'FBX'

    def process(self, bundle_info):
        if self._warning():
            return
        from collections.abc import Iterable
        import io_scene_fbx.export_fbx_bin as fbx
        from io_scene_fbx.fbx_utils import get_bid_name

        def get_blenderID_name(bid):
            if isinstance(bid, Iterable):
                for i, e in enumerate(bid):
                    if i == len(bid) - 1:
                        return get_bid_name(e)
            else:
                return get_bid_name(bid)
        fbx.get_blenderID_name = get_blenderID_name

    def post_export(self, bundle_info):
        if self._warning():
            return
        import io_scene_fbx.export_fbx_bin as fbx
        import io_scene_fbx.fbx_utils as utils
        fbx.get_blenderID_name = utils.get_blenderID_name
