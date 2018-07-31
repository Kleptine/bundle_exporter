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

		ModelImporter.useFileScale = false;
		ModelImporter.globalScale = 1.0f;
		ModelImporter.swapUVChannels = false;
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