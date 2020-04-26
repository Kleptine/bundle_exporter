from . import modifier_rename
from . import modifier_merge
from . import modifier_copy_modifiers
from . import modifier_collider
from . import modifier_LOD
from . import modifier_vertex_ao
from . import modifier_offset_transform

local_variables = locals()
modifier_modules = [local_variables[x] for x in local_variables if x.startswith('modifier_')]
modifiers = [module.Modifier() for module in modifier_modules]

from . import modifier
modifier.modifiers = modifiers

def draw(layout, context, modifiers):
	col = layout.column()

	for modifier in modifiers:
		box = col.box()
		modifier.draw(box)

	r = col.row()
	r.enabled = False

	count = 0
	for modifier in modifiers:
		if modifier.get("active"):
			count+=1