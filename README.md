# FBX Bundle Addon #

The FBX Bundle Addon is a Blender 2.79 addon to export your object selection as bundled FBX files.

**Features**
* Batch export objects in bundles of FBX files
* Bundle objects by name, group, material or scene
* Set FBX files origin to first name, bottom center or scene 0,0,0 origin
* Draw fences around objects bunbdles


![](https://farm1.staticflickr.com/787/40907228092_b74d8b8f90_o.png)

## Download ##
dsada:

**Installation**
1. Download the FBX Bundle Addon
2. In Blender from the **File** menu open **User Preferences** ![](http://renderhjs.net/textools/blender/img/installation_open_preferences.png) 
3. Go to the **Add-ons** tab ![](http://renderhjs.net/textools/blender/img/installation_addons.png).
4. Hit **Install Addon-on from File...** ![](http://renderhjs.net/textools/blender/img/installation_install_addon_from_file.png) and Select the zip file.
5. Enable the FBX Bundle Addon
6. The FBX Bundle panel can be found in the **3D view tools panel**





---

# Draw Fences #
...


---

# Bundle Types #
There are different modes of sorting your object selection into different bundles:

## Name ##
Bundles objects by matching names. Names are split by ; , . or spaces and matched by all of their name elements except the last. Sequence patterns of copied objects like .001, .002 are stripped automatically.

**Examples:**

**Object Names** | **Filename**
--- | ---
*grip.001, grip_1, grip 2* | grip
*wheel rim, wheel bolts.001 | wheel

## Group ##
Sorts by matching group names. File names are the group names of the selected objects.

## Material ##
...

## Scene ##
...




---

# Pivot Types #
## First Child ##
First object sorted by name of the group.
## Bottom Center ##
Bottom center of the bounds of the group.
## Scene Origin ##
The Scene center 0,0,0


