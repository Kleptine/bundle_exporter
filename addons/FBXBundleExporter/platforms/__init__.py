from . import platform_unity
from . import platform_gltf
from . import platform_unreal
from . import platform_blender


platforms = {
	'UNITY' : platform_unity.Platform(),
	'GLTF' : platform_gltf.Platform(),
	'UNREAL' : platform_unreal.Platform(),
	'BLENDER' : platform_blender.Platform()
}
