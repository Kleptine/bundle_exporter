using UnityEditor;
using UnityEngine;

public class PostprocessorMeshes : AssetPostprocessor {

	private void OnPreprocessModel() {
		if (ModelImporter.assetPath.Contains("Resources")) {
		}
		ModelImporter.importMaterials = false;
		ModelImporter.importBlendShapes = false;
		//ModelImporter.importAnimation = false;

		ModelImporter.useFileScale = false;
		ModelImporter.globalScale = 1.0f;
		ModelImporter.swapUVChannels = false;
	}

	private void OnPostprocessModel(GameObject gameObject) {
		//Collect all render components and offset their X- rotation by 90
		Renderer[] renders = gameObject.GetComponentsInChildren<Renderer>(true);
		foreach (Renderer render in renders) {
			render.transform.localEulerAngles += Vector3.right * 90f;
			if (Mathf.Abs(render.transform.localEulerAngles.x) <= 0.02) {
				render.transform.localEulerAngles = new Vector3(0f, render.transform.localEulerAngles.y, render.transform.localEulerAngles.z);
			}
		}
	}

	public Material OnAssignMaterialModel(Material material, Renderer renderer) {
		//Reference: https://forum.unity3d.com/threads/assetpostprocessor-onassignmaterialmodel-c.188278/
		string name = material.name;
		if (name.Length > 0 && name.Contains(".")) {
			name = name.Substring(0, name.IndexOf("."));
		}

		string path = "_Page2Car/Assets/Materials/" + name + ".mat";
		Material loadedMaterial = UtilitiesEditor.LoadAsset<Material>(path);
		if (loadedMaterial != null) {
			return loadedMaterial;
		} else {
			if (name.Length > 0) {
				Debug.LogWarning("Unkown material: " + name + ".mat for " + renderer.name);
			}
		}

		return null;
	}

	protected ModelImporter ModelImporter {
		get {
			return (ModelImporter)assetImporter;
		}
	}
}