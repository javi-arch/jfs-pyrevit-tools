# -*- coding: utf-8 -*-
__title__   = "Export schedule"
__doc__     = """Version = 1.0
Date     = 27.10.2025
________________________________________________________________
Description:

EN - This tool exports a schedule containing the “Family and Type” field to an Excel file, with the purpose of facilitating 
text editing of type parameters, which can later be imported back into the Revit document.
ES - Esta herramienta exporta una tabla de planificación con campo de 'Familia y tipo' a un archivo Excel con el objetivo 
de facilitar su edición de texto en parámetros de tipo que posteriormente podrán ser importados al documento de Revit.
________________________________________________________________
How-To:

EN - Select the schedule to be exported and choose the Excel file where it will be saved.
ES - Seleccionar la tabla de planificación a exportar y seleccionar el archivo de Excel en el que hacerlo.
________________________________________________________________
TODO:

- New functionalities as they arise. Currently, the tool is complete.
________________________________________________________________
Last Updates:

- [27.10.2025] v1.0 Tool complete.
________________________________________________________________
Author: Javier Fidalgo Saeta"""

#pylint: disable=C0103,E0401


# IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS

from pyrevit import forms

from rpw.ui.forms import *
import xlsxwriter

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *

import os

#.NET Imports
import clr

clr.AddReference('System')


# VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document
active_view = doc.ActiveView

selection = uidoc.Selection         #type: Selection


# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


# 1️⃣ SELECT VIEW SCHEDULE WITH 'FAMILY AND TYPE' FIELD AND SELECT EXCEL FILE

# All ViewSchedules in the document
all_vs = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Schedules).WhereElementIsNotElementType().ToElements()

viewSchedules = []              # Schedules to choose from
viewSchedules_name = []         # Names of schedules to choose from

for vs in all_vs:
    for i in range(vs.Definition.GetFieldCount()):
        try:                                        # Try block because not all parameters have .GetSchedulableField()
            field = vs.Definition.GetField(i)
            if not field.IsHidden:
                schedField = field.GetSchedulableField()
                if schedField:
                    # Check if the parameter ID corresponds to 'Family and Type'
                    if schedField.ParameterId == ElementId(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM):
                        viewSchedules.append(vs)
                        viewSchedules_name.append(vs.Name)
                        break

        except Exception as ex:
            # Simply ignore this field
            pass


if not viewSchedules:
    forms.alert("EN - No schedules found with the 'Family and Type' field visible "
                "(essential for the tool to function).\n\n"
                "ES - No se han encontrado tablas de planificación con el campo 'Familia y tipo' visible "
                "(imprescindible para el funcionamiento de la herramienta)."
                , exitscript=True)

res = forms.SelectFromList.show(viewSchedules_name,title="Schedules with 'Family and Type' field added and visible",
                                button_name='Select Schedule')

# Obtain the corresponding element
if res:
    index = viewSchedules_name.index(res)
    vs_sel = viewSchedules[index]
else:
    forms.alert("No schedule was selected."
                , exitscript=True)

file_path = select_file('Excel File (*.xlsx)|*.xlsx')

if not file_path:
    forms.alert("No Excel file was selected."
                , exitscript=True)


# 2️⃣ GET EXPORT DATA AND IMPORT CODE

t = vs_sel
table = t.GetTableData().GetSectionData(SectionType.Body)

nRows = table.NumberOfRows
nColumns = table.NumberOfColumns
#Collect data
dataListRow = []
for row in range(nRows):
    dataListColum = []
    for column in range(nColumns):
        dataListColum.append(TableView.GetCellText(t, SectionType.Body, row, column))
    dataListRow.append(dataListColum)

t_flds_code = []
for i in range(t.Definition.GetFieldCount()):
    if not t.Definition.GetField(i).IsHidden:
        try:                                    # Try block because not all parameters have .GetSchedulableField() - e.g., calculated parameters
            fld_code = t.Definition.GetField(i).GetSchedulableField().ParameterId.Value
            t_flds_code.append(str(fld_code))
        except Exception as ex:
            fld_code = str(t.Definition.GetField(i).FieldType) + "-noedit"
            t_flds_code.append(fld_code)

# ADDING IMPORT CODE
data = dataListRow

sep = "_" # If changed, it must also be changed in the import tool
code_imp = sep.join(t_flds_code)
data.append([""])
data.append(["Import Code (do not modify):"])
data.append([code_imp])

# Data to be exported
matrix = data

# 3️⃣ CREATE EXCEL SHEET AND OPEN

try:
    xlwb = xlsxwriter.Workbook(file_path)
    xlsheetname = "EXP FYT"

    xlsheet = xlwb.add_worksheet(xlsheetname)
    for idx, data in enumerate(matrix):
        xlsheet.write_row(idx, 0, data)

    xlwb.close()

    # Open the Excel file
    os.startfile(file_path)

except Exception as ex:
    forms.alert("Something went wrong with the Excel file. Make sure it’s closed."
                , exitscript=True)