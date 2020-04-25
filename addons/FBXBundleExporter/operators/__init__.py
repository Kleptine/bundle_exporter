from .op_fence_clear import BGE_OT_fence_clear
from .op_fence_draw import BGE_OT_fence_draw
from .op_file_copy_unity_script import BGE_OT_unity_script
from .op_file_export_recent_clear import BGE_OT_export_recent_clear
from .op_file_export_recent import BGE_OT_export_recent
from .op_file_export import BGE_OT_file_export
from .op_file_import import BGE_OT_file_import
from .op_file_open_folder import BGE_OT_file_open_folder
from .op_modifier_apply import BGE_OT_modifier_apply
from .op_pivot_ground import BGE_OT_pivot_ground
from .op_tool_geometry_fix import BGE_OT_tool_geometry_fix
from .op_tool_pack_bundles import BGE_OT_tool_pack_bundles
from .op_debug import BGE_PT_debug_lines, BGE_PT_debug_setup
from .op_bundles import BGE_OT_remove, BGE_OT_select

operators = [   BGE_OT_fence_clear, 
				BGE_OT_fence_draw,
				BGE_OT_unity_script,
				BGE_OT_export_recent_clear,
				BGE_OT_export_recent,
				BGE_OT_file_export,
				BGE_OT_file_import,
				BGE_OT_file_open_folder,
				BGE_OT_modifier_apply,
				BGE_OT_pivot_ground,
				BGE_OT_tool_geometry_fix,
				BGE_OT_tool_pack_bundles,
				BGE_PT_debug_lines,
				BGE_PT_debug_setup,
				BGE_OT_remove,
				BGE_OT_select
				]