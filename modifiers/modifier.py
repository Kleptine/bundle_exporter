import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

from ..settings import prefix_copy


class BGE_mod_default(bpy.types.PropertyGroup):
    unique_num = 0  # this is used by the "add modifier" operator for creating the enum
    label = "Modifier"
    id = 'modifier'  # unique id for each modifier
    url = ""
    type = "MESH"  # HELPER / MESH / ARMATURE / GENERAL
    icon = 'MODIFIER'
    priority = 200  # lower number will be executed earlier
    tooltip = 'Default modifier'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )

    def __lt__(self, other):
        return self.priority < other.priority

    @classmethod
    def settings_name(cls):
        return "BGE_modifier_{}".format(cls.id)

    @classmethod
    def settings_path_global(cls):
        return "bpy.context.preferences.addons['{}'].preferences.modifier_preferences.BGE_modifier_{}".format(__name__.split('.')[0], cls.id)

    # children of this class should implement this function to draw their settings
    def _draw_info(self, layout):
        pass

    # to make the modifier appear red return true
    def _warning(self):
        return False

    def draw(self, layout, active_as_x=True):
        row = layout.row(align=True)
        if not active_as_x:
            row.prop(self, "active", text="")
        else:
            row.prop(
                self,
                'show_info',
                icon="TRIA_DOWN" if self.show_info else "TRIA_RIGHT",
                icon_only=True,
                text='',
                emboss=False
            )
        if self._warning():
            row.alert = True

        row.label(text="{}".format(self.label), icon=self.icon)

        r = row.row(align=True)
        r.enabled = self.active
        r.alignment = 'RIGHT'
        # r.operator( BGE_OT_modifier_apply.bl_idname, icon='FILE_TICK' ).modifier_id = self.id

        r = row.row(align=True)
        r.alert = False
        r.alignment = 'RIGHT'

        if bpy.context.preferences.addons[__name__.split('.')[0]].preferences.show_help:
            r.operator('bge.modifier_info', emboss=False, icon='INFO', text='').modifier_name = self.id

        if active_as_x:
            r.prop(self, "active", text="", icon='X', icon_only=True, emboss=False)
        # r.operator("wm.url_open", text="", icon='QUESTION').url = self.url

        if(self.active and self.show_info):
            row = layout.row()
            row.separator()
            row.separator()
            col = row.column(align=False)
            self._draw_info(col)

    def get_object_from_name(self, name):
        try:
            return next(x for x in bpy.data.objects if x.name == name or ('__orig_name__' in x and x['__orig_name__'] == name))
        except StopIteration:
            return None

    def process(self, bundle_info):
        # do changes to bundle
        pass

    def post_export(self, bundle_info):
        pass
