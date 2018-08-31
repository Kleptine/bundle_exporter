import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

from . import modifier_merge
from . import modifier_copy_modifiers
from . import modifier_collider
from . import modifier_LOD
from . import modifier_vertex_ao

# from . import modifier_rename

import imp
imp.reload(modifier_merge) 
imp.reload(modifier_copy_modifiers) 
imp.reload(modifier_collider) 
imp.reload(modifier_LOD) 
imp.reload(modifier_vertex_ao) 

# imp.reload(modifier_rename) 

modifiers = list([
	modifier_merge.Modifier(),
	modifier_copy_modifiers.Modifier(),
	modifier_collider.Modifier(),
	modifier_LOD.Modifier(),
	modifier_vertex_ao.Modifier(),
])