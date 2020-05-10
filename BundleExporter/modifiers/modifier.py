import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

from ..settings import prefix_copy


class BGE_mod_default(bpy.types.PropertyGroup):
    unique_num = 0
    label = "Modifier"
    id = 'modifier'
    url = ""
    type = "MESH"
    global_settings = True
    icon = 'MODIFIER'
    priority = 200  # lower number will be executed earlier

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    def __lt__(self, other):
        return self.priority < other.priority

    @classmethod
    def settings_name(cls):
        return "BGE_modifier_{}".format(cls.id)

    @classmethod
    def settings_path_global(cls):
        return "bpy.context.preferences.addons['{}'].preferences.modifier_preferences.BGE_modifier_{}".format(__name__.split('.')[0], cls.id)

    def draw(self, layout):
        row = layout.row(align=True)
        row.prop(self, "active", text="")
        row.label(text="{}".format(self.label), icon=self.icon)

        r = row.row(align=True)
        r.enabled = self.active
        r.alignment = 'RIGHT'
        # r.operator( BGE_OT_modifier_apply.bl_idname, icon='FILE_TICK' ).modifier_id = self.id

        r = row.row(align=True)
        r.alignment = 'RIGHT'
        r.operator("wm.url_open", text="", icon='QUESTION').url = self.url

    def print(self):
        pass
        # print("Modifier '{}'' mode: {}".format(label, mode))

    def get_object_from_name(self, name):
        source = None
        if name in bpy.data.objects.keys():
            source = bpy.data.objects[name]
        if prefix_copy + name in bpy.data.objects.keys():
            source = bpy.data.objects[prefix_copy + name]
        return source

    def process_objects(self, name, objects, helpers, armatures):
        return objects, helpers, armatures, []

    def process_name(self, name):
        return name

    def process_pivot(self, pivot, objects, helpers, armatures):
        return pivot

    def process_path(self, name, path):
        return path
