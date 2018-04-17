using System.IO;
using UnityEditor;
using UnityEngine;

public class PostprocessorMeshes : AssetPostprocessor {

	protected ModelImporter ModelImporter {
		get {
			return (ModelImporter)assetImporter;
		}
	}

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

			//Snap to 0 if close to 0
			if (Mathf.Abs(render.transform.localEulerAngles.x) <= 0.02) {
				render.transform.localEulerAngles = new Vector3(0f, render.transform.localEulerAngles.y, render.transform.localEulerAngles.z);
			}
		}
	}

	public Material OnAssignMaterialModel(Material material, Renderer renderer) {
		string name = material.name;
		if (name.Length > 0 && name.Contains(".")) {
			name = name.Substring(0, name.IndexOf("."));
		}

		//Find all project materials, and match by name
		string[] materialIDs =  AssetDatabase.FindAssets("t:Material");

		foreach (string materialID in materialIDs) {
			string path = AssetDatabase.GUIDToAssetPath(materialID);
			string extension = Path.GetExtension(path);
			if (extension == ".mat") {
				string nameMaterial = Path.GetFileNameWithoutExtension(path);
				if (nameMaterial == name) {
					return AssetDatabase.LoadAssetAtPath<Material>(path);
				}
			}
		}

		//Crate Empty material?

		return null;
	}
}