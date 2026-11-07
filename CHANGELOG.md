# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-11-07

### Added

- A sample model saved in Revit 2027 and the shared parameters file, in the `samples` folder.

### Changed

- The README says the tools were built for Revit 2025 and last tested on Revit 2027.

### Removed

- The ribbon screenshot in the README, which showed the old button names.

## [1.0.0] - 2026-10-25

First tagged release.

### Added

- MIT license.
- Button metadata: author, minimum Revit version (2024) and a help link that F1 opens.
- The Help button links to the documentation.

### Changed

- The README now covers requirements, installation and every tool, with a summary in Spanish.
- The "Excel - type parameters editing" panel is now called "Excel".
- Button names use title case: Export Schedule, Import Text Data, Create Type Marks and Update Type Marks.

### Fixed

- Import Text Data matched parameter ids partially, so a value could be written to the wrong type parameter. Ids must now match exactly.
- Typos in the Spanish messages of the fire evacuation and legend tools.

### Removed

- Unused sample code, snippets and a disabled Import CAD hook from a pyRevit starter kit.
- The Tests button.

## Tool history before 1.0.0

Each button keeps its own version number in its tooltip.

- **2026-02-21:** README with the list of tools and a screenshot of the ribbon.
- **2026-02-20:** first upload to GitHub.
- **2026-01-30:** Create Counts and Update Counts v1.0. Update Type Marks v1.1 draws arrows from each text note to its legend component.
- **2025-10-29:** Evacuation Stairs v1.0, for simple width cases (P/160, at least 1.00 m).
- **2025-10-27:** Export Schedule and Import Text Data v1.0.
- **2025-10-17:** Create Type Marks and Update Type Marks v1.0.
- **2025-09-05:** Evacuation Doors v1.1 adds the people coming from doors and stairs at the start of each route.
- **2025-08-28:** Evacuation Doors v1.0.

[1.1.0]: https://github.com/javi-arch/jfs-pyrevit-tools/releases/tag/v1.1.0
[1.0.0]: https://github.com/javi-arch/jfs-pyrevit-tools/releases/tag/v1.0.0
