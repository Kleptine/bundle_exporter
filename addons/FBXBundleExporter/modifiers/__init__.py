from . import modifier
from . import modifier_rename
from . import modifier_merge
from . import modifier_copy_modifiers
from . import modifier_collider
from . import modifier_LOD
from . import modifier_vertex_ao
from . import modifier_offset_transform

modifiers = list([
	modifier_rename.Modifier(),
	modifier_offset_transform.Modifier(),
	modifier_copy_modifiers.Modifier(),
	modifier_merge.Modifier(),
	modifier_collider.Modifier(),
	modifier_LOD.Modifier(),
	modifier_vertex_ao.Modifier(),
])


modifier.modifiers = modifiers