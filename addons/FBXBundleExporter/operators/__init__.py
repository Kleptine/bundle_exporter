# ---------------------------------------------------------------------------- #
#                     AUTO LOAD ALL OPERATORS IN SUBMODULES                    #
# ---------------------------------------------------------------------------- #
import os
import importlib
tree = [x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x.endswith('.py')]

for i in tree:
    importlib.import_module('.'+i, package=__package__)

__globals = globals().copy()

operators = []

for x in [x for x in __globals if x.startswith('op_')]:
	for y in [item for item in dir(__globals[x]) if item.startswith('BGE_')]:
		op = getattr(__globals[x], y)
		globals()[y] = op
		operators.append(op)

# ---------------------------------------------------------------------------- #
#                              register/unregister                             #
# ---------------------------------------------------------------------------- #

def register():
	print('--> REGISTER OPERATORS')
	from bpy.utils import register_class
	for operator in operators:
		register_class(operator)
		
def unregister():
	print('### UNREGISTER OPERATORS')
	from bpy.utils import unregister_class
	for operator in operators:
		unregister_class(operator)