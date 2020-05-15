import bpy
import imp

from . import modifier


class BGE_mod_set_origin(modifier.BGE_mod_default):
    label = "Set Origin"
    id = 'set_origin'
    url = "http://renderhjs.net/fbxbundle/"
    type = 'MESH'
    icon = 'OBJECT_ORIGIN'
    tooltip = 'Applies the pivot of the bundle to all the meshes (changes their origin)'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    def draw(self, layout):
        super().draw(layout)
        if(self.active):
            pass

    def process(self, bundle_info):
        # TODO: needs to be implemented
        pass
