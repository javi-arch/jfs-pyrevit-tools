# -*- coding: utf-8 -*-
# IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

# .NET Imports (You often need List import)
import clr

clr.AddReference("System")
from System.Collections.Generic import List

import re # para herramientas de modificar texto - copia de ChatGPT

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

active_view = doc.ActiveView

# REUSABLE SNIPPETS

def markfromlegcom(legcom_element): # OBTIENE LA MARCA DE TIPO DEL TIPO ORIGINARIO DE UN COMPONENTE DE LEYENDA

    # OBTENER PARÁMETRO (.LEGEND_COMPONENT) DEL COMPONENTE EN EL QUE APARECE LA FAMTYP ORIGINARIA
    legcom_type = legcom_element.get_Parameter(BuiltInParameter.LEGEND_COMPONENT)

    txt = legcom_type.AsValueString() #OBTENEMOS EL VALOR EN TEXTO - PERO NO COINCIDE EXACTAMENTE EN FORMATO CON EL VALOR DEL .ELEM_FAMILY_AND_TYPE_PARAM DE LOS ELEMENTOS EN MODELO
    txtmod = re.sub(r"^[^:]+:\s*(.*?)\s*:\s*", r"\1: ", txt) #MODIFICAMOS EL TEXTO PARA PODER FILTRAR CON EQUALS ...

    # FILTER - OBTENEMOS SU CORRESPONDIENTE ELEMENTO EN MODELO

    p_famtyp_id = ElementId(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
    f_param = ParameterValueProvider(p_famtyp_id) # FUNCIÓN PARA SACAR EL PRIMER VALOR A COMPARAR

    evaluator = FilterStringEquals() # EVALUADOR DE IGUALDAD
    value = txtmod # VALOR ORIGINAL A COMPARAR
    f_rule = FilterStringRule(f_param, evaluator, value) # NORMA DE FILTRO

    filter_famtyp = ElementParameterFilter(f_rule) # FILTRO
    realelements = FilteredElementCollector(doc).WherePasses(filter_famtyp).WhereElementIsNotElementType().ToElements() # OBTENEMOS TODOS LOS ELEMENTOS DE ESA FAMTYP

    instance = realelements[0] # NOS QUEDAMOS CON UN SÓLO ELEMENTO (INSTANCE) PARA TRABAJAR CON ÉL

    # SACAR MARCA DE TIPO - NOTA DE TEXTO

    type = doc.GetElement(instance.GetTypeId()) # OBTENEMOS EL TIPO
    mark = type.get_Parameter(BuiltInParameter.WINDOW_TYPE_ID) # OBTENEMOS MARCA DE TIPO
    return mark