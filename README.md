# JFS Tools for pyRevit

[![Revit 2024+](https://img.shields.io/badge/Revit-2024%2B-0696D7)](#requirements)
[![pyRevit extension](https://img.shields.io/badge/pyRevit-extension-E05A2B)](https://github.com/pyrevitlabs/pyRevit)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A [pyRevit](https://github.com/pyrevitlabs/pyRevit) extension that adds a **JFS** tab to the Revit ribbon. Its buttons export and import type parameter text with Excel, keep legend annotations in sync with the model, and size evacuation doors and stairs under the Spanish building code (CTE DB-SI).

<img width="897" alt="The JFS tab in the Revit ribbon" src="https://github.com/user-attachments/assets/2fe5d4de-4f09-4694-9556-b9b3c0edf0c4" />

> **Context.** I wrote these tools in 2025, with the last updates in January 2026, while learning the Revit API through pyRevit. Each one automates a task I used to do by hand in real projects. Today an AI assistant could write similar scripts in minutes; I keep them here as a record of how I solved each problem at the time.

## Tools

| | Panel | Button | What it does |
|:-:|---|---|---|
| <img src="JFS-tools.extension/JFS.tab/Excel.panel/Export%20Schedule.pushbutton/icon.png" width="32" alt=""> | Excel | [Export Schedule](#export-schedule) | Exports a schedule to Excel so the text of type parameters can be edited there. |
| <img src="JFS-tools.extension/JFS.tab/Excel.panel/Import%20Text%20Data.pushbutton/icon.png" width="32" alt=""> | Excel | [Import Text Data](#import-text-data) | Writes the edited text back to the type parameters. |
| <img src="JFS-tools.extension/JFS.tab/Legends.panel/Create%20Type%20Marks.pushbutton/icon.png" width="32" alt=""> | Legends | [Create Type Marks](#create-type-marks) | Labels each legend component with the type mark of its type. |
| <img src="JFS-tools.extension/JFS.tab/Legends.panel/Update%20Type%20Marks.pushbutton/icon.png" width="32" alt=""> | Legends | [Update Type Marks](#update-type-marks) | Updates those labels when type marks change. |
| <img src="JFS-tools.extension/JFS.tab/Legends.panel/Create%20Counts.pushbutton/icon.png" width="32" alt=""> | Legends | [Create Counts](#create-counts) | Labels each legend component with how many instances of its type the project has. |
| <img src="JFS-tools.extension/JFS.tab/Legends.panel/Update%20Counts.pushbutton/icon.png" width="32" alt=""> | Legends | [Update Counts](#update-counts) | Updates those counts. |
| <img src="JFS-tools.extension/JFS.tab/Fire%20Evacuation.panel/Evacuation%20Doors.pushbutton/icon.png" width="32" alt=""> | Fire Evacuation | [Evacuation Doors](#evacuation-doors) | Calculates the occupancy and minimum width of an evacuation door. |
| <img src="JFS-tools.extension/JFS.tab/Fire%20Evacuation.panel/Evacuation%20Stairs.pushbutton/icon.png" width="32" alt=""> | Fire Evacuation | [Evacuation Stairs](#evacuation-stairs) | Calculates the occupancy and minimum width of an evacuation stair. |

The **Home** panel adds a link to my website and a **Help** button with contact details. Every message the tools show is in English and Spanish.

## Requirements

- **Revit 2024 or later.** The scripts use API members that Revit 2024 introduced, such as `ElementId.Value`. I developed and used them on Revit 2025.
- **pyRevit**, in a version that supports your Revit, running scripts on its default IronPython 2.7 engine.
- Nothing else to install: `xlsxwriter`, `xlrd` and `rpw`, used by the Excel tools, ship with pyRevit.

## Installation

1. Download this repository with **Code → Download ZIP** and unzip it, or clone it:

   ```bash
   git clone https://github.com/javi-arch/jfs-pyrevit-tools.git
   ```

2. In Revit, open **pyRevit → Settings**. Under **Custom Extension Directories**, add the `jfs-pyrevit-tools` folder, the one that contains `JFS-tools.extension`.
3. Click **Save Settings and Reload**. The **JFS** tab appears in the ribbon.

If you prefer the pyRevit command line, `pyrevit extensions paths add "C:\path\to\jfs-pyrevit-tools"` does step 2. To update the tools later, download the repository again (or run `git pull`) and reload pyRevit.

## Using the tools

Hover over a button to read its full description, or press **F1** while hovering to open its section of this page.

### Excel

#### Export Schedule

Exports a schedule to an `.xlsx` file and opens it, so the text of type parameters can be edited in Excel.

- The list only shows schedules where the **Family and Type** field is visible, because that column is how each row finds its type again.
- Edit the cells, but keep rows and columns where they are. The last row holds an import code that Import Text Data needs: leave it as it is.

#### Import Text Data

Reads a file created with Export Schedule and writes the changes back to the model.

- It only updates type parameters that store text and are not read-only. Numbers, lengths and other kinds of values are skipped.
- A progress bar shows each row as it is imported, and you can cancel it.

### Legends

All four buttons work on the active legend view.

#### Create Type Marks

Places a text note with the type mark of the source type at the center of every legend component. It uses the text type `Type mark Text` if the project has it, and any other text type if not.

#### Update Type Marks

Rewrites the type mark notes that no longer match the model.

- It only checks unpinned notes of the `Type mark Text` type. Pin a note to protect it.
- You choose the grid format of the legend (square, vertical or horizontal) and where the notes sit relative to their components (positions 1 to 9). The tool uses this to link each note to the nearest component in that direction.
- It draws an arrow from each note to its component so you can check the links: orange when the link is unique, red when several notes point to the same component. The arrows are filled regions of the types `aux_orange` and `aux_red`; delete them when you are done.

#### Create Counts

Works like Create Type Marks, but each note shows how many instances of the source type the project has (for example, `12 units`). It uses the text type `Count Text`.

#### Update Counts

Works like Update Type Marks, for `Count Text` notes.

### Fire Evacuation

These tools apply the evacuation rules of the Spanish building code, CTE DB-SI. Before running them:

- Create the shared parameters `NUMBER PEOPLE` (Integer) and `MINIMUM WIDTH` (Length), discipline Common, for the Doors and Stairs categories.
- Optionally, create `UPWARD EVACUATION` (Yes/No) for Stairs, to mark stairs that evacuate upwards, and `ADDS OCCUPANCY` (Yes/No) for Spaces, to leave out spaces that do not add occupancy.
- Draw every evacuation route with **Path of Travel** lines, and model the MEP **Spaces** with their occupancy.
- Put routes and spaces on the level of the door you analyze or, for a stair, on the level where people enter it.

#### Evacuation Doors

Select an evacuation door. The tool adds up the occupancy of the spaces crossed by the routes that end at that door, plus the people already assigned to the doors and stairs where those routes start. It writes the total to `NUMBER PEOPLE` and the minimum width to `MINIMUM WIDTH` (P/200, at least 0.80 m), and tells you whether the current width of the door complies.

#### Evacuation Stairs

Select an evacuation stair. It works like Evacuation Doors and also adds the people coming down (or up) from the previous stair, so run it in the order in which people evacuate. It covers the simple case of unprotected stairs that evacuate downwards (P/160, at least 1.00 m).

> These tools help check a design; they do not replace a professional review against the code.

## Repository structure

```text
JFS-tools.extension/
└── JFS.tab/
    ├── Home.panel/              Website, Help
    ├── Excel.panel/             Export Schedule, Import Text Data
    ├── Legends.panel/           Create and Update Type Marks, Create and Update Counts
    └── Fire Evacuation.panel/   Evacuation Doors, Evacuation Stairs
```

Each button is a folder with its `script.py` and `icon.png`, following the pyRevit bundle conventions. The `bundle.yaml` files set the order of panels and buttons. Version history is in [CHANGELOG.md](CHANGELOG.md).

## Resumen en español

**Herramientas JFS** es una extensión de pyRevit que añade la pestaña **JFS** a la cinta de Revit, con botones para:

- **Excel:** exportar una tabla de planificación a Excel, editar allí el texto de los parámetros de tipo y volver a importarlo al modelo.
- **Leyendas:** crear y actualizar notas de texto con la marca de tipo o el número de ejemplares de cada componente de leyenda.
- **Evacuación de incendios:** calcular la ocupación y el ancho mínimo de puertas y escaleras de evacuación según el CTE DB-SI.

Todos los mensajes de las herramientas están en inglés y en español. Requiere Revit 2024 o posterior. Para instalarla, descarga el repositorio y añade su carpeta en **pyRevit → Settings → Custom Extension Directories**.

Las desarrollé en 2025, con las últimas mejoras en enero de 2026, mientras aprendía la API de Revit con pyRevit.

## License

[MIT](LICENSE) © 2025-2026 Javier Fidalgo Saeta

## Author

**Javier Fidalgo Saeta**, architect and BIM specialist: [javierfidalgosaeta.com](https://javierfidalgosaeta.com) · [LinkedIn](https://www.linkedin.com/in/jafisa/) · [GitHub](https://github.com/javi-arch)
