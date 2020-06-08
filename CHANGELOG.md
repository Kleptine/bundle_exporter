# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.3](https://gitlab.com/AquaticNightmare/bundle_exporter/-/releases/2_1_3)
### Added
- Option for merge meshes to merge UVs by index instead of by name
- New Pivot option "From Collection" it will get the pivot from the collection instance_offset parameter (Properties->Object->Collection->X,Y,Z)

### Fixed
- Fixed error using the "Export Textures" modifier (it would cause error when finding a texture node without an image applied to it)
- UI stopped working when adding the Master Collection as a bundle (Master Collection bundles are deliberately not supported)

## [2.1.2](https://gitlab.com/AquaticNightmare/bundle_exporter/-/releases/2_1_2)
### Fixed
- Unity export preset fixed

## [2.1.1](https://gitlab.com/AquaticNightmare/bundle_exporter/-/releases/2_1_1) - 2020-06-03
### Fixed
- Children of objects are now correctly exported (the bundle pivot was being applied to both parents and children)
- Error when drawing fences when "Export actions as files" is active
- Objects hidden in the view layer are now correclty exported

### Changed
- Some UI changes

## [2.1.0](https://gitlab.com/AquaticNightmare/bundle_exporter/-/releases/2_1_0) - 2020-05-31
### Added
- New modifiers:
    - "Export actions as files" (only FBX) creates separate fbx files with an armature and an animation each (for game development)
- "Merge Armatures" modifier now deletes the created actions after exporting
- Added auto updater

### Fixed
- Drivers from sub collections are now kept when using "Instanced collections to objects" modifier
- Fixed error when trying to select a bundle with one of its objects hidden by an excluded collection

## [2.0.1](https://gitlab.com/AquaticNightmare/bundle_exporter/-/releases/2_0_1) - 2020-05-30
### Added
- New modifiers:
    - "Keep action names". For exporting actions in FBX, it avoids adding the object name before the action name.
    - "Export textures". It will export all textures being used by the materials of the exported objects to the export path (useful when they are embeded).
- Option to remove duplicate numbering (".001", ".002", ".003"...) for the "Rename" modifier
- "Copy modifiers" modifier now shows the modifiers in a list
- "Merge Meshes" modifier searches for exportable armatures if a mesh being exported has an invalid "Armature" modifier and tries to fix it
- Easy access to scene unit system and scale in the main panel
- New button that shows the modifier tooltip (It can be disabled in the addon preferences)
- Changelog

### Fixed
- Fixed issues when baking actions with the "Merge armatures" modifier
- Drawing fences now takes into account modifiers (for pivots and names for example)
- Drivers are now kept when using the "Instanced collections to objects" modifier
- Error when using the "Exclude from export" modifier
- Actions are no longer duplicated when exporting an object with an active action

### Changed
- More UI changes for the bundles (more compact and easier to read)

## [2.0.0](https://gitlab.com/AquaticNightmare/bundle_exporter/-/releases/2_0_0) - 2020-05-16
### Added
- Support for exporting **empties**
- Support for exporting **armatures**
- Defaults for modifiers can now be saved in the addon preferences
- Each bundle has its own **Override modifiers**. These have preference over the modifiers added to the scene
- New modifiers:
    - "Custom pivot": uses the origin of the provided source object as the new pivot for the bundle
    - "Transform empties": lets you apply a scale to all the empties (useful for exporting into unreal)
    - "Instance collections to objects" (support for **instanced collections**)
    - "Merge armatures" (and actions)
    - "Exclude from export": lets you choose if non-selectable/invisible objects or collections should be exported
- Modifiers now show a description when hovering over them inside the dropdown
- Modifiers now show an icon to better identify them
- Each bundle has its own "Bundle by" and "Pivot from" options
- Option to merge by collection or by parent for the "Merge Meshes" modifier
- Option to keep armature for the "Merge Meshes" modifier
- Export format OBJ

### Changed
- Bundles are now stored in the blend file and are not based on current selection
- Modifiers are now added from a dropdown
- Bundles are now selected from a list
- Export platform was changed to "Export format" and "Export preset"

### Fixed
- Hidden and unselectable objects and collections are now correctly exported

### Removed
- The apply modifiers operator
- The unity script
- "Move pivots to ground" operator