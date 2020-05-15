import bpy
import bmesh
import imp

from . import modifier


class BGE_mod_custom_pivot(modifier.BGE_mod_default):
    label = "Custom Pivot"
    id = 'custom_pivot'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'MESH'
    icon = 'EMPTY_ARROWS'
    priority = 10
    tooltip = 'Assign a custom pivot based on the chosen source object'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )
    source: bpy.props.StringProperty()

    def draw(self, layout):
        super().draw(layout)
        if(self.active):
            # Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects

            row = layout.row(align=True)
            row.separator()
            row.separator()

            row.prop_search(self, "source", bpy.context.scene, "objects", text="Source")

    def process(self, bundle_info):
        source = self.get_object_from_name(self.source)
        if source:
            bundle_info['pivot'] = source.location

        