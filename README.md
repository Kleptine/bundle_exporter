# FBX Bundle Addon #

The **FBX Bundle** Addon is a **Blender 2.79** addon that simplifies the process of batch exporting FBX files. It's easy to use: specify a folder, select your objects, press 'Export'. FBX files for Unity will have correct rotations and scale values assigned as well as automatically existing materials assigned if their names match with Blender's materials per object.

## Features ##

* **Export** selected objects as FBX bundles
* **Import** 3D files from a folder
* **Preview** of export files as you select objects
* **Bundle objects** by name, group, material or scene
* Set file **pivots** to: first object, bottom center or scene origin
* **Draw fences** around bundles of objects


////![] (https://farm1.staticflickr.com/787/40907228092_b74d8b8f90_o.png)

## Download ##

* [FBX_Bundle_1.0.0.zip](http://renderhjs.net/textools/blender/Blender_TexTools_0.9.0.zip)

## Installation ##

1. Download the FBX Bundle Addon
2. In Blender from the **File** menu open **User Preferences** ![](http://renderhjs.net/textools/blender/img/installation_open_preferences.png) 
3. Go to the **Add-ons** tab ![](http://renderhjs.net/textools/blender/img/installation_addons.png).
4. Hit **Install Addon-on from File...** ![](http://renderhjs.net/textools/blender/img/installation_install_addon_from_file.png) and Select the zip file.
5. Enable the **FBX Bundle** Addon
6. The FBX Bundle panel can be found in the **3D view tools panel**


---

# Draw Fences #
Draws grease pencil lines around your selected object bundles.

* The border uses the padding from the settings
* The pole represents the bundle origin when exporting FBX files
* A thin grid is drawn to seperate within a bundle

Use the red '**x**' button to clear the fence drawings.

////![] (https://farm1.staticflickr.com/787/40907228092_b74d8b8f90_o.png)


---

# Export #
Exports the selected FBX bundles to the specified directory.


# Import #
Import all selected 3D files from the specified directory. Supported file types are:

* fbx
* obj
* 3ds



---

# Bundle Types #
At the core of this addon objects are bundled by common traits. Bundles are listed in the interfaces as FBX files. There are different modes of sorting your object selection into bundles:

## Name ##
Bundles objects by matching names. Names are split by ; , . spaces or camelCase and matched by all of their name elements except the last. Sequence patterns of copied objects like .001, .002 are stripped automatically.

**Examples:**

**Object Names** | **Filename**
--- | ---
*grip.001, grip_1, grip 2* | grip
*wheel rim, wheel bolts.001 | wheel

## Group ##
Bundles objects by matching group names.

## Material ##
Bundles objects by matching materials. This mode can be useful for texture painting or baking.

## Scene ##
Bundles selected objects of the current scene. This is the easiest option to export all objects into a single FBX file.


---

# Pivot Types #
## First Child ##
Use the pivot of the first object sorted by name.
## Bottom Center ##
Bottom center of the bounds of the group.
## Scene Origin ##
The Scene center 0,0,0


---

# Working with Unity #

The addon comes with an Unity Editor script which automatically resets the -90 degree rotations and assigns existing materials automatially if the name assigned in blender matches any material name in your Unity project.

**Copying Unity Editor script**

1. In Blender from the **File** menu open **User Preferences** ![](http://renderhjs.net/textools/blender/img/installation_open_preferences.png) 
2. Go to the **Add-ons** tab ![](http://renderhjs.net/textools/blender/img/installation_addons.png).
3. In the search field enter **'FBX Bundle'**
4. Inside the FBX Bundle addon panel press the 'Copy Unity Script' buttn
5. Browse for your Unity assets project folder and confirm

The script will create an 'Editor' folder with a C# script inside called 'PostprocessorMeshes.cs'. This script modifies the FBX file object inside Unity each time the file gets re-imported or updated.

