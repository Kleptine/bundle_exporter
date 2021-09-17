import bpy

class BGE_OT_add_batch(bpy.types.Operator):
    """Create new bundle"""
    bl_idname = "bge.add_batch"
    bl_label = "Add Batch"

    def execute(self, context):
        bpy.context.scene.BGE_Settings.batches.add()
        return {'FINISHED'}