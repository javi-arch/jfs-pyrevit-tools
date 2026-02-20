# -*- coding: utf-8 -*-
__title__   = "Import text data"
__doc__     = """Version = 1.0
Date     = 27.10.2025
________________________________________________________________
Description:

EN - This tool imports modifications to Type parameter text values, made in an Excel file previously exported from a schedule.
ES - Esta herramienta importa modificaciones en el texto de parámetros de tipo, realizadas en una exportación de tabla de planificación a un archivo Excel.
________________________________________________________________
How-To:

EN - Select the Excel file that was exported using the 'Export schedule' tool.
ES - Seleccionar el archivo Excel en el que se ha realizado la exportación con la herramienta 'Exportar tabla'.
________________________________________________________________
TODO:

- New functionalities as they arise. Currently, the tool is complete.
________________________________________________________________
Last Updates:

- [27.10.2025] v1.0 Tool complete.
________________________________________________________________
Author: Javier Fidalgo Saeta"""


# IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS

from Autodesk.Revit.DB import *

from Autodesk.Revit.DB import StorageType

import clr

clr.AddReference('System')


from rpw.ui.forms import *

import xlrd

from pyrevit import forms
from pyrevit.forms import ProgressBar


# VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

active_view = doc.ActiveView


# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


# 1️⃣ READ EXCEL

file_path = select_file('Excel File (*.xlsx)|*.xlsx')

if not file_path:
    forms.alert("No Excel file was selected."
                , exitscript=True)

workbook = xlrd.open_workbook(file_path)
sheet = workbook.sheet_by_index(0)

row_count = sheet.nrows
col_count = sheet.ncols

data_all = []

for row in range(row_count):
    data = [] # Create a list for each row
    for col in range(col_count):
        data.append(sheet.cell_value(row,col))
    data_all.append(data)

# Remove lines without useful data
data = data_all[1:-3]
# Get the import code list
code_imp = data_all[-1][0].split("_")

# Get ID of 'Family and Type'
FYT_id = ElementId(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM).Value

# Get index of 'Family and Type' column
col_FYT = code_imp.index(str(FYT_id))
# Get list of parameters ...
code_params = code_imp[:col_FYT] + code_imp[col_FYT+1:]
# ... and their indices (columns) within the list
col_params = range(len(code_imp))[:col_FYT] + range(len(code_imp))[col_FYT+1:]


# 2️⃣ APPLY CHANGES

t = Transaction(doc, __title__)
t.Start()

all_elems = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()

# Progress Bar setup ...

max_value = len(data)  # Total number of rows
with ProgressBar(title='Importing data ... ({value} of {max_value})', cancellable=True) as pb:
    for counter, row in enumerate(data):
        # If the user cancels the progress bar
        if pb.cancelled:
            break

        # For each row ...
        FYT = row[col_FYT]

        # If "Family and Type" contains ":", it's an element of interest
        if ":" in FYT:
            row_elems = [
                e for e in all_elems
                if e.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
                and e.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM).AsValueString() == FYT
            ]
            if not row_elems:
                continue

            # Pick any element of that Family/Type
            e = row_elems[0]
            # Get its Type
            typ = doc.GetElement(e.GetTypeId())

            # For each parameter, check if it's a Type parameter (exists) and if it's editable
            for code, col in zip(code_params, col_params):
                # Only numbers (Id codes)
                try:
                    code_int = int(code)
                except Exception as ex:
                     continue

                t_param = False
                for p in typ.Parameters:
                    # Compare each param: If code in Id number of param
                    if code in str(p.Id.Value):
                        t_param = p
                        break

                if not t_param or t_param.IsReadOnly:
                    continue

                value = row[col]

                # Check if it is a String and if it's different from the existing value
                if t_param.StorageType == StorageType.String:
                    if t_param.AsString() != str(value):
                        t_param.Set(str(value))

        # 🔹 Update progress
        pb.update_progress(counter + 1, max_value)

t.Commit()