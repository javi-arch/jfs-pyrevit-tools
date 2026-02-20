# -*- coding: utf-8 -*-
__title__   = "Create Counts"
__doc__     = """Version = 1.0
Date     = 30.01.2026
________________________________________________________________
Description:

EN - This tool creates a text note for each legend component found in the current view, displaying the total count of its instances in the project.
ES - Esta herramienta crea una nota de texto para cada componente de leyenda que encuentra en la vista actual con el recuento de sus instancias en proyecto.
________________________________________________________________
How-To:

EN - The tool detects the source family and type of each legend component and creates a text note at the center of the component with the count of its instances in the project.
ES - La herramienta detecta la familia y tipo origen de cada componente de leyenda y crea en el centro del componente una nota de texto con el recuento de sus instancias en proyecto.
________________________________________________________________
TODO:

- New functionalities as they arise. Currently, the tool is complete.
________________________________________________________________
Last Updates:

- [30.01.2026] v1.0 Tool complete.
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
# Flag to warn if the specific type "Count Text" is missing
msg = 1

text_types = FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()

for text_type in text_types:
    if text_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() == "Count Text":
        text_type_id = text_type.Id
        msg = 0
        break # Exit loop once the correct type is found

if msg:
    forms.alert("EN - This tool is designed to create text notes of type 'Count Text'. This type does not exist in the document, so a default type will be used.\n\n"
                "ES - Esta herramienta está diseñada para crear notas de texto de tipo 'Count Text'. Este tipo no existe en el documento por lo que se utilizará otro cualquiera.", exitscript=False)


# 2️⃣ FUNCTION TO GET COUNT FROM LEGEND COMPONENTS

def countfromlegcom(legcom_element):
    """ OBTAINS THE INSTANCE COUNT OF THE SOURCE TYPE OF A LEGEND COMPONENT """

    legcom_type = legcom_element.get_Parameter(BuiltInParameter.LEGEND_COMPONENT)

    type_id = legcom_type.AsElementId()

    all_elems = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()

    count = 0
    for e in all_elems:
        if e.GetTypeId() == type_id:
            count += 1

    return count

# 3️⃣ CREATE COUNT TEXT NOTES

t = Transaction(doc,__title__)

t.Start()

# GET ALL LEGEND COMPONENTS IN VIEW
all_legcom_in_view = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_LegendComponents).WhereElementIsNotElementType().ToElementIds()

for legcom_id in all_legcom_in_view:

    # GET COUNT OF THE SOURCE TYPE VIA FUNCTION:

    # The function input must be a Legend Component element (not its ID)
    legcom_element = doc.GetElement(legcom_id)

    try:
        # Obtain the count
        count = countfromlegcom(legcom_element)
        text = str(count)
        text_u = text + " units"

    except Exception as e:
        print("Error calculating count: {}".format(e))
        text_u = "ERROR"


    # TEXT NOTE LOCATION

    bb = legcom_element.get_BoundingBox(active_view) # BOUNDING BOX OF THE LEGEND COMPONENT
    pt = (bb.Max + bb.Min) / 2 # CENTER POINT FOR TEXT NOTE PLACEMENT

    # CREATE TEXT NOTE
    TextNote.Create(doc, active_view.Id, pt, text_u, text_type_id)

t.Commit()