import bpy
import os
import mathutils

bl_info = {
 "name": "FBX Bundle Exporter",
 "description": "Export object selection in FBX bundles",
 "author": "Hendrik Schoenmaker",
 "blender": (2, 7, 9),
 "version": (0, 1, 0),
 "category": "Import-Export",
 "location": "3D Viewport tools panel: FBX Bundle Exporter",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
}


class UnityBatchExportPanel(bpy.types.Panel):

	bl_idname = "FBX_bundle_exporter_panel"
	bl_label = "FBX Bundle Exporter"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = "objectmode"
	# bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):

		layout = self.layout
		layout.label(text="Exporting UI")
		
			
# registers
def register():
	bpy.utils.register_class(UnityBatchExportPanel)

def unregister():
	bpy.utils.unregister_class(UnityBatchExportPanel)

if __name__ == "__main__":
	register()
