# FBX Bundle Addon #

The **FBX Bundle** Addon is a **Blender 2.79** addon that simplifies the process of batch exporting FBX files. It's easy to use: specify a folder, select your objects, press 'Export'. FBX files for Unity will have correct rotations and scale values assigned as well as automatically existing materials assigned if their names match with Blender's materials per object.

## Download ##

* [FBX_Bundle_1.1.0.zip](http://renderhjs.net/blender/fbx_bundle/FBX_Bundle_1.1.0.zip)


## Features ##

* **Batch Export** selected objects as FBX bundles
* **Batch Import** 3D files from a folder
* **Templates** for Unity, Unreal and Blender
* **Preview** FBX bundles as you select objects
* **Bundle objects** by name, group, material or scene
* **Fix Unity** rotation, scale and material issues
* **Draw fences** around bundles of objects
* **Align pivots** to common ground


![](http://renderhjs.net/blender/fbx_bundle/overview.gif)


## Installation ##

1. Download the FBX Bundle Addon
2. In Blender from the **File** menu open **User Preferences** ![](http://renderhjs.net/textools/blender/img/installation_open_preferences.png) 
3. Go to the **Add-ons** tab ![](http://renderhjs.net/textools/blender/img/installation_addons.png).
4. Hit **Install Addon-on from File...** ![](http://renderhjs.net/textools/blender/img/installation_install_addon_from_file.png) and Select the zip file.
5. Enable the **FBX Bundle** Addon
6. The FBX Bundle panel can be found in the **3D view tools panel**


---

# Draw Fences #

![](https://farm1.staticflickr.com/812/40627267655_540fe2a5b3_o.png)

Draws grease pencil lines around your selected object bundles.

* The border uses the padding from the settings
* The pole represents the bundle origin when exporting FBX files
* A thin grid is drawn to seperate objects within a bundle

Use the red '**x**' button to clear the fence drawings.

![](https://farm1.staticflickr.com/866/40806993094_dc2d16dbac_o.png)

---

# Ground pivot #

![](https://farm1.staticflickr.com/909/40858121474_6fdd7c9e23_o.png)

Sets the pivot points of selected objects to the ground of the bounding box of the bundle.

![](https://farm1.staticflickr.com/861/39761054960_6dd0a411a9_o.gif)

---

# Export #

![](https://farm1.staticflickr.com/939/26650599827_7b38a2c414_o.png)

Exports the selected FBX bundles to the specified directory.

**Note** By default the addon will export FBX files aimed for the Unity engine. You can change the target platform settings.

![](https://farm1.staticflickr.com/842/41528382392_55f776a7aa_o.gif)


## Merge ##

![](https://farm1.staticflickr.com/887/39711493860_b652128fb1_o.png)

When merge is enabled all objects of a bundle are merged into a single mesh when exporting.

---

# Import #

![](https://farm1.staticflickr.com/837/27649976458_abae4ffddf_o.png)

Import all selected 3D files from the specified directory. Supported file types are:

* fbx
* obj
* 3ds



---


# Bundle Types #

![](https://farm1.staticflickr.com/807/40626971555_77035ddd60_o.png)

At the core of this addon objects are bundled by common traits. Bundles are listed in the interfaces as FBX files. There are different modes of sorting your object selection into bundles:

### Name ###
Bundles objects by matching names. Names are split by ; , . spaces or camelCase and matched by all of their name elements except the last. Sequence patterns of copied objects like .001, .002 are stripped automatically.

**Examples:**

**Object Names** | **Filename**
--- | ---
*grip.001, grip_1, grip 2* | grip
*wheel rim, wheel bolts.001 | wheel

### Group ###
Bundles objects by matching group names.

### Parent ###
Bundles objects by matching parent object. For each object the most parent object is used.

### Material ###
Bundles objects by matching materials. This mode can be useful for texture painting or baking.

### Scene ###
Bundles selected objects of the current scene. This is the easiest option to export all objects into a single FBX file.


---

# Pivot Types #

![](https://farm1.staticflickr.com/826/39711247600_eed039c5d7_o.png)

Determines the origin point for each exported FBX file.

### First Child ###
Use the pivot of the first object sorted by name.
### Bottom Center ###
Bottom center of the bounds of the group.
### Scene Origin ###
The Scene center 0,0,0


---

# Working with Unity #

The addon comes with an Unity Editor script which automatically resets the -90 degree rotations and assigns existing materials automatially if the name assigned in blender matches any material name in your Unity project. This script is completely optional and not mandatory at all.

![](https://farm1.staticflickr.com/925/39763685890_aa1801d581_o.png)


**Copying Unity Editor script**

1. In Blender from the **File** menu open **User Preferences** ![](http://renderhjs.net/textools/blender/img/installation_open_preferences.png) 
2. Go to the **Add-ons** tab ![](http://renderhjs.net/textools/blender/img/installation_addons.png).
3. In the search field enter **'FBX Bundle'**
4. Inside the FBX Bundle addon panel press the '**Copy Unity Script**' button 
5. Browse for your Unity assets project folder and confirm

![](https://farm1.staticflickr.com/934/39760671570_e9bbe13f6c_o.png)

The script will create an 'Editor' folder with a C# script inside called '**PostprocessorMeshes.cs**'. This script modifies the FBX file object inside Unity each time the file gets re-imported or updated.

Alternatively the C# script can also be found in the addon zip file under "*FBXBundleExporter/resources/PostprocessorMeshes.cs*"

### Auto assigning materiarls ###
The Unity Editor script can automatically assign existing materials if the material names between Blender and the Unity project match.

![](http://renderhjs.net/blender/fbx_bundle/unity_material_matching.gif)

