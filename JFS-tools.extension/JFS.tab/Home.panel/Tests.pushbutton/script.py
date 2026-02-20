# -*- coding: utf-8 -*-
__title__   = "Tests"
__doc__     = """Version = 0.0
Date     = 00.00.0000
________________________________________________________________
Description:

Script for tests.
________________________________________________________________
Author: Javier Fidalgo Saeta"""


# IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List
from pyrevit import forms


# VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


msg = "Hello Revit"
forms.alert(msg, exitscript=True)


# SELECT ELEMENT
# sel = uidoc.Selection.PickObject(ObjectType.Element)
# el = doc.GetElement(sel)







