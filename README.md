# JFS tools for Revit (pyRevit)

Custom toolbar for Revit developed with **pyRevit**. It includes the following analysis and process automation tools:

* **Excel - type parameters editing**
    * **Export schedule:**
      This tool exports a schedule containing the “Family and Type” field to an Excel file, with the purpose of facilitating text editing of type parameters, which can later be imported back into the Revit document.
    * **Import text data:**
      This tool imports modifications to Type parameter text values, made in an Excel file previously exported from a schedule.

* **Legends**
    * **Create Type marks:**
      This tool creates a text note displaying the Type Mark for every legend component found in the current view.
    * **Update Type marks:**
      This tool updates Type Mark text notes corresponding to legend components found in the current view.
    * **Create Counts:**
      This tool creates a text note for each legend component found in the current view, displaying the total count of its instances in the project.
    * **Update Counts:**
      This tool updates count text notes corresponding to legend components found in the current view.

* **Fire Evacuation**
    * **Evacuation Doors:**
      This tool calculates the number of people for which a floor or building evacuation door must be dimensioned, automatically filling in its 'MINIMUM WIDTH' and 'NUMBER PEOPLE' parameters.
    * **Evacuation Stairs:**
      This tool calculates the number of people for which an evacuation staircase must be dimensioned, automatically filling its 'MINIMUM WIDTH' and 'NUMBER PEOPLE' parameters.

---

### Dependencies
To use these tools, the [pyRevit plugin](https://pyrevitlabs.notion.site/) must be installed in Revit, and the folder where they are located must be linked to the Custom Extension Directories so that **pyRevit** can recognize them properly.

### Preview
<img width="897" height="107" alt="img-preview-JFS-tools" src="https://github.com/user-attachments/assets/2fe5d4de-4f09-4694-9556-b9b3c0edf0c4" />

---

**Author:** Javier Fidalgo Saeta  
**Platform:** Revit 25 + pyRevit
