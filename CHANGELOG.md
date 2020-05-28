# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1](https://gitlab.com/AquaticNightmare/bundle_exporter/-/tree/2.0.1) - 2020-05-30
### Added
- Option to remove duplicate numbering (".001", ".002", ".003"...) for the "Rename" modifier
- "Copy modifiers" modifier now shows the modifiers in a list
- Changelog

### Fixed
- Fixed issues when baking actions with the "Merge armatures" modifier
- Drawing fences now takes into account modifiers (for pivots and names for example)
- Drivers are now kept when using the "Instanced collections to objects" modifier

### Changed
- More UI changes for the bundles (more compact and easier to read)

## [2.0.0](https://gitlab.com/AquaticNightmare/bundle_exporter/-/tree/6ff629e451a8c6b0562c4f37556f9489b5b61e25) - 2020-05-16
### Added
- Support for exporting **empties**
- Support for exporting **armatures**
- Defaults for modifiers can now be saved in the addon preferences
- Each bundle has its own **Override modifiers**. These have preference over the modifiers added to the scene
- New modifiers:
    - "Custom pivot"
    - "Transform empties"
    - "Instance collections to objects" (support for **instanced collections**)
    - "Merge armatures" (and actions)
    - "Exclude from export" (lets you choose if non-selectable/invisible objects or collections should be exported)
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