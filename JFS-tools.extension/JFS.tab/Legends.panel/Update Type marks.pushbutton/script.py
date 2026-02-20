# -*- coding: utf-8 -*-
__title__   = "Update Type marks"
__doc__     = """Version = 1.1
Date     = 30.01.2026
________________________________________________________________
Description:

EN - This tool updates Type Mark text notes corresponding to legend components found in the current view.
ES - Esta herramienta actualiza las notas de texto de marcas de tipo respective a componentes de leyenda que se encuentran en la vista actual.
________________________________________________________________
How-To:

EN - The tool detects Type Mark text notes and associates them with a nearby legend component. 
It then checks the Type Mark of the component's source type and, if necessary, updates the text note.
ES - La herramienta detecta las notas de texto de marcas de tipo y las asocia con un componente de leyenda cercano. 
Después comprueba la marca de tipo del tipo origen del componente y, si es necesario, la actualiza en la nota de texto.
________________________________________________________________
TODO:

- New functionalities as they arise. Currently, the tool is complete.
________________________________________________________________
Last Updates:

- [17.10.2025] v1.0 Tool complete.
- [30.01.2026] v1.1 Addition of auxiliary arrows to visualize the link between each text note and its legend component..
________________________________________________________________
Author: Javier Fidalgo Saeta"""


# IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS

from types import ObjectType


from Autodesk.Revit.DB import *

from Autodesk.Revit.DB import XYZ

from pyrevit import forms

import math

import re

import sys

import clr
from rpw.db import FamilyInstance

from System.Collections.Generic import List

from collections import Counter

clr.AddReference('System')


# VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

active_view = doc.ActiveView


# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


# 0️⃣ WELCOME MESSAGE

res = forms.alert("EN - This tool updates Type Mark text notes corresponding to families with "
"legend components in the current view. Before proceeding, consider the following conditions "
"for correct operation:\n\n"

"- Ensure that Type Marks use the correct text note type: Type mark Text. "
"The tool only checks these specific notes to avoid modifying other annotations.\n\n"
                  
"- The tool only considers unpinned (unlocked) text. To prevent updating specific marks, "
"you can pin their corresponding text note.\n\n"

"- The tool relies on user input regarding the format and positioning of legend elements. "
"In irregular configurations, variable formats, or very tall/wide cells, the tool may fail. "
"Manual identification is recommended for these special cases by pinning the text note to prevent errors.\n\n\n"
                  
"ES - Esta herramienta actualiza las notas de texto de marcas de tipo respective a familias con"
" componentes de leyenda en la vista actual. Antes de continuar ten en cuenta las siguientes condiciones para su "
"correcto funcionamiento:\n\n"

"- Asegúrate de que las marcas de tipo están en el tipo de nota de texto correspondiente: Type mark Text. "
"La herramienta solo se fijará en estos textos para evitar modificar otras anotaciones.\n\n"
                  
"- La herramienta solo tendrá en cuenta textos desbloqueados. Para evitar la actualización de una o varias marcas de tipo"
" puedes bloquear su nota de texto correspondiente.\n\n"

"- La herramienta tiene en cuenta la información aportada por el usuario sobre el formato y posicionamiento de los elementos de la leyenda. "
" En configuraciones irregulares, con formatos variables o celdas muy altas o anchas, la herramienta puede fallar. Se recomienda la identificación"
" de estos casos especiales para su actualización manual, bloqueando la nota de texto para evitar la modificación errónea por parte de la herramienta.\n\n",

options=["Cancel", "Continue"])

if res == "Cancel":
    sys.exit()


# 1️⃣ DETECT TYPE MARK 'TAGS' AND LEGEND COMPONENTS

msg = 1

text_types = FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()

for text_type in text_types:
    if text_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() == "Type mark Text":
        msg = 0
        break # Correct type found

if msg:
    forms.alert("The text note type 'Type mark Text' was not found in the document."
          , exitscript=True)


# GET ALL TEXT NOTES IN VIEW
all_txtnt_in_view = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()
# Filter by type and pinning status
txtnts = [tn for tn in all_txtnt_in_view if tn.Name == 'Type mark Text' and not tn.Pinned]

if not txtnts:
    forms.alert("No editable text notes of type 'Type mark Text' were found in the legend."
          , exitscript=True)


# GET ALL LEGEND COMPONENTS IN VIEW
all_legcom_in_view = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_LegendComponents).WhereElementIsNotElementType().ToElements()


# 2️⃣ PROMPT FOR APPROXIMATE POSITION OF TYPE MARKS

forms.alert("EN - It is necessary to indicate the approximate format of the legend grid:\n\n"
            "S - square / V - vertical / H - horizontal\n(if format is variable, S - square is recommended)\n\n"
            "It is also necessary to indicate the approximate position of the text notes relative to their corresponding component:\n\n"
            "         1         2         3           \n"
            "                ╔════╗                 \n"
            "                ║        ║                \n"
            "         4     ║   5  ║    6           \n"
            "                ║        ║                \n"
            "              ═╩════╩═                 \n"
            "         7         8         9           \n\n"
            "In the next window, select the code that best fits the actual format and position:\n\nS/V/H - 1/2/3/4/5/6/7/8/9\n\n\n"
            "ES - Es necesario indicar el formato aproximado de las cuadrículas de la leyenda:\n\n"
            "S - cuadrado  / V - vertical / H - horizontal\n(si el formato es variable, mejor indicar S - cuadrado)\n\n"
            "También es necesario indicar la posición aproximada de los textos de marca de tipo respecto de su componente correspondiente. "
            "En la siguiente ventana selecciona el código que más se aproxime al formato y posición real:\n\nS/V/H - 1/2/3/4/5/6/7/8/9"
            , exitscript=False)


pos = ['S-1','S-2','S-3','S-4','S-5','S-6','S-7','S-8','S-9',
        'V-1','V-2','V-3','V-4','V-5','V-6','V-7','V-8','V-9',
       'H-1','H-2','H-3','H-4','H-5','H-6','H-7','H-8','H-9']


res = forms.SelectFromList.show(pos, button_name='Select position')


vecs = [(1,-1,0),(0,-1,0),(-1,-1,0),(1,0,0),(0,0,0),(-1,0,0),(1,1,0),(0,1,0),(-1,1,0),
       (1.732,-1,0),(0,-1,0),(-1.732,-1,0),(1,0,0),(0,0,0),(-1,0,0),(1.732,1,0),(0,1,0),(-1.732,1,0),
       (1,-1.732,0),(0,-1,0),(-1,-1.732,0),(1,0,0),(0,0,0),(-1,0,0),(1,1.732,0),(0,1,0),(-1,1.732,0)]

try:

    # Find the corresponding index
    idx = pos.index(res)
    # Get the associated vector
    vec = vecs[idx]

except:
    forms.alert("An option must be selected to run the tool."
                , exitscript=True)


# 3️⃣ DETECT LOCATION OF TEXTS AND COMPONENTS

# Text coordinates
txtnt_pts = []
for tn in txtnts:
    pt = tn.Coord
    txtnt_pts.append(pt)

# Center points of components
all_legcom_pts = []
for alc in all_legcom_in_view:
    bb = alc.get_BoundingBox(active_view)  # BOUNDING BOX OF LEGCOM
    pt = (bb.Max + bb.Min) / 2  # CENTER POINT FOR CALCULATION
    all_legcom_pts.append(pt)


# 4️⃣ CALCULATE NEAREST COMPONENT BASED ON DIRECTION

# Iterate through all text notes and find the corresponding component for each

mag = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2) # vector length

lc_respective = []
lc_pt_respective = []


# Check if the vector has length to apply directional distance

if mag == 0:
    for tn_pt in txtnt_pts:
        lc = None
        lc_pt = None
        lc_d = float("inf")

        for alc, alc_pt in zip(all_legcom_in_view, all_legcom_pts):
            delta = tn_pt - alc_pt
            dist = delta.GetLength()

            if dist < lc_d:
                lc = alc
                lc_pt = alc_pt
                lc_d = dist

        lc_respective.append(lc)
        lc_pt_respective.append(lc_pt)

else:
    vec = XYZ(-1*(vec[0]/mag), -1*(vec[1]/mag), -1*(vec[2]/mag))        # UNIT VECTOR

    margen_deg = 30     # ANGLE WITHOUT PENALTY
    penal_max = 20      # MAXIMUM PENALTY

    for tn_pt in txtnt_pts:
        lc = None
        lc_pt = None
        lc_d = float("inf")

        for alc, alc_pt in zip(all_legcom_in_view, all_legcom_pts):
            delta = tn_pt - alc_pt
            dist = delta.GetLength()

            if dist != 0:
                # Calculate angle between vec and delta
                delta_unit = delta.Normalize()
                dot = vec.DotProduct(delta_unit)
                dot = max(-1.0, min(1.0, dot))  # avoid numerical errors
                ang = math.degrees(math.acos(dot))

                # Penalty based on angle
                if ang <= margen_deg:
                    penal = 1.0
                else:
                    # Quadratic penalty (adjustable)
                    penal = 1.0 + (penal_max - 1.0) * ((ang - margen_deg) / (180 - margen_deg)) ** 2

                dist = dist * penal

            if dist < lc_d:
                lc = alc
                lc_pt = alc_pt
                lc_d = dist

        lc_respective.append(lc)
        lc_pt_respective.append(lc_pt)


# 5️⃣ SEPARATE LEGEND COMPONENTS LINKED MORE THAN ONCE

counts_lc = Counter(lc_respective)

lc_rep = []
lc_pt_rep = []
lc_un = []
lc_pt_un = []
txtnts_rep = []
txtnt_pts_rep = []
txtnts_un = []
txtnt_pts_un = []

for i in range(len(lc_respective)):
    item = lc_respective[i]
    point = lc_pt_respective[i]
    item_t = txtnts[i]
    point_t = txtnt_pts[i]

    if counts_lc[item] > 1:
        # If it appears more than once, it goes to repeated lists
        lc_rep.append(item)
        lc_pt_rep.append(point)
        txtnts_rep.append(item_t)
        txtnt_pts_rep.append(point_t)
    else:
        # If it appears once, it goes to unique lists
        lc_un.append(item)
        lc_pt_un.append(point)
        txtnts_un.append(item_t)
        txtnt_pts_un.append(point_t)


# 6️⃣ FUNCTIONS

def markfromlegcom(legcom_element):
    """ OBTAINS THE TYPE MARK FROM THE SOURCE TYPE OF A LEGEND COMPONENT """

    legcom_type = legcom_element.get_Parameter(BuiltInParameter.LEGEND_COMPONENT)

    type_id = legcom_type.AsElementId()
    type = doc.GetElement(type_id)  # OBTAIN THE TYPE
    # OBTAIN THE TYPE MARK PARAMETER
    mark_param = type.get_Parameter(BuiltInParameter.WINDOW_TYPE_ID)

    return mark_param

def arrowfrom2pts(pt1,pt2):
    """ RETURNS A REVIT CURVELOOP OBJECT """

    # 1. Arrow configuration
    head_length = 1.5  # Head length
    head_width = 1.0  # Head width
    shaft_width = 0.2  # Shaft width

    # 2. Vector calculations
    direction = (pt2 - pt1).Normalize()
    # Perpendicular vector for width (assuming View XY plane)
    normal = XYZ.BasisZ
    side_vec = direction.CrossProduct(normal).Normalize()

    # Geometry key points
    p_base_head = pt2 - direction * head_length

    # Outline vertices
    v1 = pt1 + side_vec * (shaft_width / 2.0)  # Shaft start right
    v2 = p_base_head + side_vec * (shaft_width / 2.0)  # Shaft shoulder right
    v3 = p_base_head + side_vec * (head_width / 2.0)  # Head wing right
    v4 = pt2  # Final tip
    v5 = p_base_head - side_vec * (head_width / 2.0)  # Head wing left
    v6 = p_base_head - side_vec * (shaft_width / 2.0)  # Shaft shoulder left
    v7 = pt1 - side_vec * (shaft_width / 2.0)  # Shaft start left

    points = [v1, v2, v3, v4, v5, v6, v7]

    # 3. Create CurveLoop
    curves = []
    for i in range(len(points)):
        p_start = points[i]
        p_end = points[(i + 1) % len(points)]  # Close loop with the first point
        curves.append(Line.CreateBound(p_start, p_end))

    curveloop = CurveLoop.Create(curves)

    return curveloop

def distance_2d_XYZ(pt1, pt2):
    return math.sqrt((pt2.X - pt1.X)**2 + (pt2.Y - pt1.Y)**2)


# 7️⃣ ARROW PREPARATION

# 1. Name for new filled region types
new_type_name_r = "aux_red"
new_type_name_u = "aux_orange"

# 2. Search for an existing type to use as a template
existing_type = FilteredElementCollector(doc).OfClass(FilledRegionType).FirstElement()

# 3. Search for Fill Pattern (Solid fill)
fill_pattern = next((fp for fp in FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
                     if fp.Name == "<Solid fill>" or fp.Name == "<Relleno uniforme>"), None)

# Check if types already exist to avoid duplicate errors
check_exists_r = next((t for t in FilteredElementCollector(doc).OfClass(FilledRegionType) if t.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() == new_type_name_r),
                    None)
check_exists_u = next((t for t in FilteredElementCollector(doc).OfClass(FilledRegionType) if t.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() == new_type_name_u),
                    None)

# Lists for combined filled regions (Orange - unique cases)

curveloops_u = []
curveloops_u_revitList = List[CurveLoop]()


# 8️⃣ UPDATES

otms = []   # ORIGINAL TYPE MARKS
ntms = []   # NEW TYPE MARKS

t = Transaction(doc,__title__)

t.Start()


# RETRIEVE FILLED REGION TYPES

if not check_exists_r:
    # Duplicate existing type
    new_frt = existing_type.Duplicate(new_type_name_r)

    # Configure: Color and Pattern
    new_frt.ForegroundPatternColor = Color(255, 0, 0)  # Rojo (R, G, B)
    new_frt.ForegroundPatternId = fill_pattern.Id
    new_frt.IsMasking = True

    filled_region_type_r = new_frt

else:
    filled_region_type_r = check_exists_r

if not check_exists_u:
    # Duplicate existing type
    new_frt = existing_type.Duplicate(new_type_name_u)

    # Configure: Color and Pattern
    new_frt.ForegroundPatternColor = Color(255, 128, 0)  # Rojo (R, G, B)
    new_frt.ForegroundPatternId = fill_pattern.Id
    new_frt.IsMasking = True

    filled_region_type_u = new_frt

else:
    filled_region_type_u = check_exists_u


# ITERATE THROUGH REPEATED CASES
for tn,lc,pt1,pt2 in zip(txtnts_rep,lc_rep,txtnt_pts_rep,lc_pt_rep):
    otm = tn.Text.strip()

    try:
        # Retrieve Type Mark parameter
        ntm_param = markfromlegcom(lc)

        if ntm_param and ntm_param.AsValueString():

            ntm = ntm_param.AsValueString()
        else:
            ntm = "NO MARK"

    except Exception as e:
        print("Error extracting mark: {}".format(e))
        ntm = "ERROR"

    if otm != ntm:
        tn.SetFormattedText(FormattedText(ntm))
        otms.append(otm)
        ntms.append(ntm)

    # CREATE ARROW
    if distance_2d_XYZ(pt1, pt2) > 0.1: # Skip if arrow is too small
        curveloop = arrowfrom2pts(pt1, pt2)
        region = FilledRegion.Create(doc, filled_region_type_r.Id, active_view.Id, [curveloop])


# ITERATE THROUGH UNIQUE CASES
for tn, lc, pt1, pt2 in zip(txtnts_un, lc_un, txtnt_pts_un, lc_pt_un):
    otm = tn.Text.strip()

    try:
        # Retrieve Type Mark parameter
        ntm_param = markfromlegcom(lc)

        if ntm_param and ntm_param.AsValueString():

            ntm = ntm_param.AsValueString()
        else:
            ntm = "NO MARK"

    except Exception as e:
        print("Error extracting mark: {}".format(e))
        ntm = "ERROR"

    if otm != ntm:
        tn.SetFormattedText(FormattedText(ntm))
        otms.append(otm)
        ntms.append(ntm)

    # DATA FOR COMBINED ARROW REGION
    if distance_2d_XYZ(pt1, pt2) > 0.1:  # Skip if arrow is too small
        curveloop = arrowfrom2pts(pt1, pt2)
        curveloops_u.append(curveloop)
        curveloops_u_revitList.Add(curveloop)

# UNIQUE - ATTEMPT COMBINED REGION; OTHERWISE: INDIVIDUAL ARROWS
try:
    region = FilledRegion.Create(doc, filled_region_type_u.Id, active_view.Id, curveloops_u_revitList)

except:
    for cl in curveloops_u:
        region = FilledRegion.Create(doc, filled_region_type_u.Id, active_view.Id, [cl])

t.Commit()

# 🔟 FINAL MESSAGE

tm_updated = len(ntms)

# Create text for changes: otm ---> ntm
changes = "\n".join(["{}  --->  {}".format(o, n) for o, n in zip(otms, ntms)])

# GET ALL TEXT NOTES IN VIEW
all_txtnt_in_view = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()

txtnts = [tn.Text[:-1] for tn in all_txtnt_in_view if tn.Name == 'Type mark Text']


# Find repeated elements in view
rep = list(set([x for x in txtnts if txtnts.count(x) > 1]))

# Filter those that were recently updated
rep_in_ntms = [x for x in rep if x in ntms]

if not rep_in_ntms:
    if tm_updated > 0:
        forms.alert(
            "{} Type Marks have been updated:\n\n{}".format(
                tm_updated, changes
            ),
            exitscript=False
        )
    else:
        forms.alert(
            "No Type Marks required updates.",
            exitscript=False
        )

else:
    rep_str = ", ".join(rep_in_ntms)
    forms.alert(
        "{} Type Marks have been updated:\n\n{}\n\n"
        "Attention: The following duplicate Type Marks were detected in the legend after execution:\n\n{}"
        .format(
            tm_updated, changes, rep_str
        ),
        exitscript=False
    )
