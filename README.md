# FBX Bundle Exporter #

FBX Bundle Exporter is a Blender 2.79 addon to export your object selection as bundled FBX files.

**Features**
* Batch export selected files
* Fence objects with gizmos
* Apply additional modifiers e.g. LOD, Merge, Add Colliders,...


![](https://farm1.staticflickr.com/787/40907228092_b74d8b8f90_o.png)
---

# Bundle Mode #
There are different modes of sorting your object selection into different bundles:

## Name ##
Bundles objects by matching names. Names are split by ; , . or spaces and matched by all of their name elements except the last. Sequence patterns of copied objects like .001, .002 are stripped automatically.

**Examples:**

**Object Names** | **Filename**
--- | ---
*grip.001, grip_1, grip 2* | grip
*wheel rim, wheel bolts.001 | wheel


## Space ##
Sorts objects by colliding bounding boxes. Objects that are placed near each other or intersect are grouped together. The filename will then be the first alphabetical object name of that group.

## Group ##
Sorts by matching group names. File names are the group names of the selected objects.



---

# Pivot Mode #
## First Child ##
First object sorted by name of the group.
## Bottom Center ##
Bottom center of the bounds of the group.
## Scene Origin ##
The Scene center 0,0,0


