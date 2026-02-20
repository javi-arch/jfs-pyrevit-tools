# -*- coding: utf-8 -*-
__title__   = "Help"
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

# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


msg = ("EN - For any questions or issues that may arise with the tools, please do not hesitate to contact the following email address:\n\njavier.fidalgo.saeta@gmail.com\n\n\n"
       "ES - Para cualquier pregunta o problema que pueda surgir con las herramientas, por favor no dude en ponerse en contacto con la siguiente dirección de correo electrónico:\n\njavier.fidalgo.saeta@gmail.com")

forms.alert(msg, exitscript=True)








