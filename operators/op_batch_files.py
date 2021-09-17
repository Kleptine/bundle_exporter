import bpy

from bpy.app.handlers import persistent

files = []
index = 0

@persistent
def load_handler(dummy):
    bpy.ops.bge.file_export()

    global index
    index +=1

    if index >= len(files):
        bpy.app.handlers.load_post.pop(bpy.app.handlers.load_post.index(load_handler))
        return
    bpy.ops.wm.open_mainfile(filepath=files[index])

class BGE_OT_batch_files(bpy.types.Operator):
    """Exports the files in the list"""
    bl_idname = "bge.batch_export"
    bl_label = "Batch Export"

    def execute(self, context):
        global files
        global index
        files = [x.path for x in  bpy.context.scene.BGE_Settings.batches]
        index = 0
        if files:
            bpy.app.handlers.load_post.append(load_handler)
            bpy.ops.wm.open_mainfile(filepath=files[0])
        return {'FINISHED'}
