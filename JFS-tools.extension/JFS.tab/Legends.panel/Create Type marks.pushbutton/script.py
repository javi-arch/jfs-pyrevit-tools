# -*- coding: utf-8 -*-
__title__   = "Create Type marks"
__doc__     = """Version = 1.0
Date     = 17.10.2025
________________________________________________________________
Description:

EN - This tool creates a text note displaying the Type Mark for every legend component found in the current view.
ES - Esta herramienta crea una nota de texto de la marca de tipo en cada componente de leyenda que encuentra en la vista actual.
________________________________________________________________
How-To:

EN - The tool detects the source family and type of each legend component and creates a text note with its Type Mark at the center of the component.
ES - La herramienta detecta la familia y tipo origen de cada componente de leyenda y crea una nota de texto con su marca de tipo en el centro del componente.
________________________________________________________________
TODO:

- New functionalities as they arise. Currently, the tool is complete.
________________________________________________________________
Last Updates:

- [17.10.2025] v1.0 Tool complete.
________________________________________________________________
Author: Javier Fidalgo Saeta"""


# IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS

from types import ObjectType

from Autodesk.Revit.DB import *

from pyrevit import forms


import re


#.NET Imports
import clr
from rpw.db import FamilyInstance


clr.AddReference('System')


# VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

active_view = doc.ActiveView


# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


# 1️⃣ TEXT TYPE TO BE USED

# By default, pick the first type found so the tool can run in any context
text_type_id = FilteredElementCollector(doc).OfClass(TextNoteType).FirstElementId()
# Flag to warn if the specific type "Type mark Text" is missing
msg = 1

text_types = FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()

for text_type in text_types:
    if text_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() == "Type mark Text":
        text_type_id = text_type.Id
        msg = 0
        break # Exit loop once the correct type is found

if msg:
    forms.alert("EN - This tool is designed to create text notes of type 'Type mark Text'. This type does not exist in the document, so a default type will be used.\n\n"
                "ES - Esta herramienta está diseñada para crear notas de texto de tipo 'Type mark Text'. Este tipo no existe en el documento por lo que se utilizará otro cualquiera.", exitscript=False)


# 2️⃣ FUNCTION TO RETRIEVE TYPE MARKS FROM LEGEND COMPONENTS

def markfromlegcom(legcom_element):
    """ OBTAINS THE TYPE MARK FROM THE SOURCE TYPE OF A LEGEND COMPONENT """

    legcom_type = legcom_element.get_Parameter(BuiltInParameter.LEGEND_COMPONENT)

    type_id = legcom_type.AsElementId()
    type = doc.GetElement(type_id)  # OBTAIN THE TYPE
    # OBTAIN THE TYPE MARK PARAMETER
    mark_param = type.get_Parameter(BuiltInParameter.WINDOW_TYPE_ID)

    return mark_param


# 3️⃣ CREATE TYPE MARKS

t = Transaction(doc,__title__)

t.Start()

# GET ALL LEGEND COMPONENTS IN VIEW
all_legcom_in_view = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_LegendComponents).WhereElementIsNotElementType().ToElementIds()

for legcom_id in all_legcom_in_view:

    # GET THE TYPE MARK FROM THE SOURCE TYPE VIA THE FUNCTION:

    # The function input must be a Legend Component Element (not its ID)
    legcom_element = doc.GetElement(legcom_id)

    try:
        # Retrieve the Type Mark parameter
        mark_param = markfromlegcom(legcom_element)

        if mark_param and mark_param.AsValueString():
            # Convert to string for the Text Note
            text = mark_param.AsValueString()
        else:
            text = "NO MARK"

    except Exception as e:
        print("Error extracting mark: {}".format(e))
        text = "ERROR"


    # TEXT NOTE LOCATION

    bb = legcom_element.get_BoundingBox(active_view) # BOUNDING BOX OF THE LEGEND COMPONENT
    pt = (bb.Max + bb.Min) / 2 # CENTER POINT FOR TEXT NOTE PLACEMENT

    # CREATE TEXT NOTE
    TextNote.Create(doc, active_view.Id, pt, text, text_type_id)

t.Commit()