import bpy

class BGE_OT_delete_batch(bpy.types.Operator):
    """"""
    bl_idname = "bge.delete_batch"
    bl_label = "Delete Batch"

    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BGE_Settings.batches.remove(self.index)
        return {'FINISHED'}