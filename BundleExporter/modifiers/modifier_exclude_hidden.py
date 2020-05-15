import bpy
import bmesh
import mathutils
import imp

from . import modifier
from .. import settings
from ..utilities import traverse_tree

exclude_types = [('HIDDEN', 'OBJECTS', 'hidden objects', 'HIDE_OFF', 2),
                 ('NOT_SELECTABLE', 'OBJECTS', 'not selectable objects', 'RESTRICT_SELECT_ON', 4),
                 ('COLLECTION_HIDDEN', 'COLLECTIONS', 'hidden collections', 'HIDE_OFF', 8),
                 ('COLLECTION_NOT_SELECTABLE', 'COLLECTIONS', 'not selectable collections', 'RESTRICT_SELECT_ON', 16)]

class BGE_mod_exclude_hidden(modifier.BGE_mod_default):
    label = "Exclude From Export"
    id = 'exclude_hidden'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'GENERAL'
    icon = 'HIDE_OFF'
    priority = -900
    tooltip = 'Exclude objects from export'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    types: bpy.props.EnumProperty(
        name="Exclude types",
        options={'ENUM_FLAG'},
        items=exclude_types,
        default={'HIDDEN', 'COLLECTION_HIDDEN'},
    )

    def draw(self, layout):
        super().draw(layout)

        row = layout.row(align=True)
        row.separator()
        row.separator()
        row.prop(self, 'types')

    def process(self, bundle_info):
        def check_export(obj):
            if 'HIDDEN' in self.types and obj['__orig_hide__']:
                return False
            if 'NOT_SELECTABLE' in self.types and obj['__orig_hide_select__']:
                return False
            coll = bpy.data.collections.get(obj['__orig_collection__'])
            if 'COLLECTION_HIDDEN' in self.types and coll and (coll['__orig_hide__'] or coll['__orig_hide_lc__'] or coll['__orig_exclude__']):
                return False
            if 'COLLECTION_NOT_SELECTABLE' in self.types and coll and coll['__orig_hide_select__']:
                return False
            return True

        bundle_info['meshes'] = [x for x in bundle_info['meshes'] if check_export(x)]
        bundle_info['empties'] = [x for x in bundle_info['empties'] if check_export(x)]
        bundle_info['armatures'] = [x for x in bundle_info['armatures'] if check_export(x)]
