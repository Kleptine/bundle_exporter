import bpy
import math
import imp

from . import modifier


class BGE_mod_collider(modifier.BGE_mod_default):
    label = "Collider Mesh"
    id = 'collider'
    url = "http://renderhjs.net/fbxbundle/#modifier_collider"
    type = 'MESH'
    icon = 'CUBE'
    priority = 999
    tooltip = 'This modifier will create extra collision meshes based on the exported meshes'

    active: bpy.props.BoolProperty(
        name="Active",
        default=False
    )

    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True
    )
    
    ratio: bpy.props.FloatProperty(
        default=0.35,
        min=0.01,
        max=1,
        description="Ratio of triangle count to orginal mesh",
        subtype='FACTOR'
    )

    angle: bpy.props.FloatProperty(
        default=40,
        min=5,
        max=55,
        description="Reduction angle in degrees",
        subtype='FACTOR'
    )

    def _draw_info(self, layout):
        row = layout.row(align=True)
        row.prop(self, "ratio", text="Ratio", icon='AUTOMERGE_ON')
        row.prop(self, "angle", text="Angle", icon='AUTOMERGE_ON')

    def process(self, bundle_info):
        # UNITY 	https://docs.unity3d.com/Manual/LevelOfDetail.html
        # UNREAL 	https://docs.unrealengine.com/en-us/Engine/Content/Types/StaticMeshes/HowTo/LODs
        # 			https://answers.unrealengine.com/questions/416995/how-to-import-lods-as-one-fbx-blender.html

        objects = bundle_info['meshes']

        for obj in objects:
            # Select
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Copy & Decimate modifier
            bpy.ops.object.duplicate()
            bpy.context.object.name = "{}_COLLIDER".format(obj.name)
            copy = bpy.context.object

            # Display as wire
            # copy.draw_type = 'WIRE'
            # copy.show_all_edges = True
            # Decimate A
            mod = copy.modifiers.new("RATIO", type='DECIMATE')
            mod.ratio = self.ratio

            # Displace
            mod = copy.modifiers.new("__displace", type='DISPLACE')
            mod.mid_level = 0.85
            mod.show_expanded = False

            # Decimate B
            mod = copy.modifiers.new("ANGLE", type='DECIMATE')
            mod.decimate_type = 'DISSOLVE'
            mod.angle_limit = self.angle * math.pi / 180

            # Triangulate
            mod = copy.modifiers.new("__triangulate", type='TRIANGULATE')
            mod.show_expanded = False

            # Triangulate
            mod = copy.modifiers.new("__shrinkwrap", type='SHRINKWRAP')
            mod.target = obj
            mod.show_expanded = False

            # bpy.ops.object.modifier_add(type='DECIMATE')
            # bpy.context.object.modifiers["Decimate"].ratio = get_quality(i, self.levels, self.quality)

            # add to export
            bundle_info['extras'].append(bpy.context.object)