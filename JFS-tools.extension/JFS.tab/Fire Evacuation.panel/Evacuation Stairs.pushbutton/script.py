# -*- coding: utf-8 -*-
__title__   = "Evacuation Stairs"
__doc__     = """Version = 1.0
Fecha    = 29.10.2025
________________________________________________________________
Description:

EN - This tool calculates the number of people for which an evacuation staircase must be dimensioned, 
automatically filling its 'MINIMUM WIDTH' and 'NUMBER PEOPLE' parameters.
ES - Esta herramienta calcula el número de personas para las que debe ser dimensionada una escalera de evacuación rellenando automáticamente sus parámetros de 'MINIMUM WIDTH' y 'NUMBER PEOPLE'.
________________________________________________________________
How-To:

EN - The tool collects the occupancies of the spaces through which the evacuation paths pass that culminate 
(end of path) at the staircase selected by the user. The paths can originate at a space exit door if permitted by regulations; the tool will detect the occupancy of this space as well.
The tool also collects the number of people evacuated from stairs or doors found at the origin of the 
evacuation paths, as well as people evacuated by upper or lower stairs, depending on the vertical 
evacuation direction.

ES - La herramienta recoge las ocupaciones de los espacios por los que pasan las rutas que culminan (fin de la ruta) en la escalera seleccionada por le usuario. Las rutas pueden tener su origen en una puerta de salida de un espacio si así se permite por normativa, la herramienta detectará la ocupación de este espacio igualmente.
La herramienta también recoge el número de personas evacuadas desde escaleras o puertas que encuentre en el origen de las rutas de evacuación, así como las personas evacuadas por escaleras superiores o inferiores, dependiendo del sentido de la evacuación vertical.
________________________________________________________________
TODO:

- Review special cases for minimum widths according to DB-SI regulations.
________________________________________________________________
Last Updates:

- [29.10.2025] v1.0 Tool assuming simple width calculation cases (min_width = max(number_people / 160.0, 1.0)).
________________________________________________________________
Author: Javier Fidalgo Saeta"""


# IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS - IMPORTS

from types import ObjectType


from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *

from pyrevit import forms

import math

import re

import sys

#.NET Imports
import clr
from rpw.db import FamilyInstance

clr.AddReference('System')
from System.Collections.Generic import List


# VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES - VARIABLES

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


def distance_2d(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


# MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN - MAIN


# 0️⃣ WELCOME MESSAGE

res = forms.alert("EN - This tool calculates the number of people for which an evacuation staircase must be dimensioned by automatically filling its 'MINIMUM WIDTH' and 'NUMBER PEOPLE' parameters. Before continuing, please note the following conditions for correct operation:\n\n"

"- Shared parameters 'MINIMUM WIDTH' (Data Type: Length) and 'NUMBER PEOPLE' (Data Type: Integer) must be created in the 'Common' discipline for the doors and stairs categories. Additionally, if there are evacuation stairs with an upward direction in the project, the 'UPWARD EVACUATION' parameter (Data Type: Yes/No) must be created (and filled) for the stairs category.\n\n"

"- All evacuation paths (Path of Travel Lines) for the floor must be drawn, and spaces (review the 'ADDS OCCUPANCY' parameter) must have their occupancy correctly assigned: the tool collects the occupancies of the spaces through which paths pass that end (PathEnd) at the staircase to be analyzed. If regulations do not require paths to end at the staircase itself, but rather at a prior compartment (e.g., protected stairs), it is recommended to use the 'Evacuation Doors' tool to calculate 'NUMBER PEOPLE' up to that compartment, then manually add the data to the staircase parameter.\n\n"

"- Paths and corresponding spaces must be associated with the same level (base or top, depending on upward "
"or downward evacuation) as the evacuation staircase to be analyzed. For example, if paths and spaces are "
"built on 'Level 1', but the top level of the evacuation staircase is 'Level 1_Terrace', the tool will fail.\n\n"
                  
"- The tool collects 'NUMBER PEOPLE' from doors and stairs where evacuation paths originate towards the staircase being analyzed. It also detects vertical evacuation continuity, collecting 'NUMBER PEOPLE' arriving from a previous staircase (lower or upper). Therefore, it is important to use the tool in the order of evacuation to ensure person loading accumulates correctly.\n\n\n"

"ES - Esta herramienta calcula el número de personas para las que debe ser dimensionada una escalera de evacuación rellenando automáticamente sus parámetros de 'MINIMUM WIDTH' y 'NUMBER PEOPLE'. Antes de continuar ten en cuenta las siguientes condiciones para su correcto funcionamiento:\n\n"

"- Deben estar creados los parámetros compartidos 'MINIMUM WIDTH' (Tipo de dato: Longitud) y 'NUMBER PEOPLE' (Tipo de dato: Entero) en disciplina 'Común', para las categorías de puertas y escaleras. Además, si existen en el proyecto escaleras de evacuación con sentido ascendente, debe estar creado (y rellenado, en su caso) el parámetro 'UPWARD EVACUATION' (Tipo de dato: Sí/No) en disciplina 'Común', para la categoría de escaleras.\n\n"

"- Todas las rutas de evacuación (Líneas de camino del recorrido) de la planta deben estar dibujadas, así como los espacios (revisar parámetro 'ADDS OCCUPANCY'), que deben tener su ocupación correctamente asignada: la herramienta recoge las ocupaciones de los espacios por los que pasan las rutas que culminan (fin de la ruta) en la escalera a analizar. En caso de que por normativa no sea necesario que las rutas culminen en la propia escalera, sino que llegan hasta una compartimentación previa (escaleras protegidas, por ejemplo), se recomienda la utilización de la herramienta 'Evacuation Doors' para el cálculo del 'NUMBER PEOPLE' hasta dicha compartimentación, para después añadir manualmente el dato al parámetro de la escalera. Las rutas pueden tener su origen en una puerta de salida de un espacio si así se permite por normativa, la herramienta detectará la ocupación de este espacio igualmente.\n\n"

"- Las rutas (Líneas de camino del recorrido) y espacios correspondientes deben estar asociados al mismo nivel (base o superior, según evacuación ascendente o descendente) que la escalera  de evacuación a analizar. Por ejemplo, si rutas y espacios están construidos en el nivel 'Level 1', pero el nivel superior de la escalera de evacuación es 'Level 1_Terrace', la herramienta fallará. En este ejemplo el nivel superior de la escalera debe ser 'Level 1', independientemente del 'Desfase superior' que pueda tener.\n\n"
                  
"- La herramienta recoge el 'NUMBER PEOPLE' de puertas y escaleras desde las que parten rutas de evacuación hasta la escalera a analizar. También detecta la continuidad vertical en la evacuación del proyecto, recogiendo el 'NUMBER PEOPLE' que llegan desde una escalera previa, inferior o superior, dependiendo del sentido de evacuación. Por esto es importante ir utilizando la herramienta en orden de evacuación, para asegurarnos de que la carga de personas se va acumulando.\n\n",

options=["Cancel", "Select stairs"])

if res == "Cancel":
    sys.exit()


# 1️⃣ SELECT THE STAIRCASE TO ANALYZE AND OBTAIN ITS RUNS, LEVELS, AND EVACUATION DIRECTION

# This method ensures only an element with the category name "stairs" is selectable:

class stair_filter(ISelectionFilter):
    def AllowElement(self, elem):
        if elem.Category.BuiltInCategory == BuiltInCategory.OST_Stairs:
            return True
try:
    sel_str = uidoc.Selection.PickObject(ObjectType.Element, stair_filter())
    stair = doc.GetElement(sel_str)
except:
    forms.alert('Nothing selected. Please select a staircase to continue.', exitscript=True)

# Parameter check

if not stair.LookupParameter('NUMBER PEOPLE'):
    forms.alert("The parameter 'NUMBER PEOPLE' does not exist in the stairs category. "
                "Add this shared parameter for the tool to function correctly.", exitscript=True)

if not stair.LookupParameter('MINIMUM WIDTH'):
    forms.alert("The parameter 'MINIMUM WIDTH' does not exist in the stairs category. "
                "Add this shared parameter for the tool to function correctly.", exitscript=True)

if not stair.LookupParameter('UPWARD EVACUATION'):
    forms.alert("The 'UPWARD EVACUATION' parameter does not exist in the stairs category. For the purposes of this tool, it will be assumed that all stairs are DOWNWARD evacuation.\n\n"
                "Add this shared parameter for the tool to work correctly if upward evacuation stairs exist.", exitscript=False)
    stair_direction = 0

elif not stair.LookupParameter('UPWARD EVACUATION').HasValue:
    forms.alert("The selected staircase does not have the 'UPWARD EVACUATION' parameter filled. "
                "For the purposes of this tool, it will be assumed that this staircase is DOWNWARD evacuation.",
                exitscript=False)
    stair_direction = 0

else:
    stair_direction = stair.LookupParameter('UPWARD EVACUATION').AsInteger()

stair_bb_max = (stair.BoundingBox[doc.ActiveView].Max.X, stair.BoundingBox[doc.ActiveView].Max.Y)
stair_bb_min = (stair.BoundingBox[doc.ActiveView].Min.X, stair.BoundingBox[doc.ActiveView].Min.Y)
stair_bb_med = (
    (stair_bb_min[0] + stair_bb_max[0]) / 2,
    (stair_bb_min[1] + stair_bb_max[1]) / 2
)

stair_levelBASE      = stair.get_Parameter(BuiltInParameter.STAIRS_BASE_LEVEL_PARAM).AsValueString()
stair_levelTOP       = stair.get_Parameter(BuiltInParameter.STAIRS_TOP_LEVEL_PARAM).AsValueString()
stair_levelBASE_id   = stair.get_Parameter(BuiltInParameter.STAIRS_BASE_LEVEL_PARAM).AsElementId()
stair_levelTOP_id    = stair.get_Parameter(BuiltInParameter.STAIRS_TOP_LEVEL_PARAM).AsElementId()

runs = list(stair.GetStairsRuns())
runs_z = []
for t in runs:
    t = doc.GetElement(t)
    runs_z.append(t.BaseElevation)
runs_arranged = [x for _, x in sorted(zip(runs_z, runs))]

runBASE_id = runs_arranged[0]
runTOP_id = runs_arranged[-1]

if stair_direction:
    stair_levelIN    = stair_levelBASE
    stair_levelOUT   = stair_levelTOP
    stair_levelIN_id = stair_levelBASE_id
    stair_levelOUT_id = stair_levelTOP_id
    runIN             = doc.GetElement(runBASE_id)
    runOUT            = doc.GetElement(runTOP_id)
    pointIN             = list(runIN.GetStairsPath())[0].GetEndPoint(0)

else:
    stair_levelIN    = stair_levelTOP
    stair_levelOUT   = stair_levelBASE
    stair_levelIN_id = stair_levelTOP_id
    stair_levelOUT_id = stair_levelBASE_id
    runIN             = doc.GetElement(runTOP_id)
    runOUT            = doc.GetElement(runBASE_id)
    pointIN             = list(runIN.GetStairsPath())[-1].GetEndPoint(1)


# 2️⃣ FIND EVACUATION PATHS THAT END AT THE STAIRCASE AND GET THEIR COMPONENT LINES

# Get evacuation paths for this level

all_paths = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PathOfTravelLines).WhereElementIsNotElementType().ToElements()
level_paths = [path for path in all_paths if path.get_Parameter(BuiltInParameter.PATH_OF_TRAVEL_LEVEL_NAME).AsString() == stair_levelIN]

# Keep those that end at the staircase

paths = [path for path in level_paths if distance_2d((path.PathEnd.X,path.PathEnd.Y),(pointIN.X, pointIN.Y)) < 3]

if not paths:
    forms.alert("No evacuation path ends at the selected staircase. You must draw evacuation paths for the floor/building before running the tool.\n\n"
                "If it is a protected staircase and paths end at its compartment door, it is recommended to run the 'Evacuation Doors' tool on those doors and manually add the sum of their 'NUMBER PEOPLE' to the staircase parameter.\n\n"
                "Alternatively, this could be a staircase connecting a floor with downward evacuation to an upper floor with upward evacuation; in which case, 'NUMBER PEOPLE' would remain at '0'.", exitscript=False)

# Get a list of all lines composing the paths (flattened)

linpaths = []
for path in paths:
    lines = list(path.GetCurves())
    for line in lines:
        linpaths.append(line)

# Get p0 and p1 of the lines

linpaths_XYZ01 = []
for line in linpaths:
    XYZ01 = [line.GetEndPoint(0), line.GetEndPoint(1)]
    linpaths_XYZ01.append(XYZ01)


# 3️⃣ COLLECT SPACES WITH LEVEL FILTERS AND 'ADDS OCCUPANCY'

all_spaces = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MEPSpaces).WhereElementIsNotElementType().ToElements()
level_spaces = [sp for sp in all_spaces if doc.GetElement(sp.LevelId).Name == stair_levelIN]

spaces = []
msg = 0
for sp in level_spaces:
    if sp.LookupParameter('ADDS OCCUPANCY') and sp.LookupParameter('ADDS OCCUPANCY').StorageType == StorageType.Integer:
        if sp.LookupParameter('ADDS OCCUPANCY').HasValue:
            if sp.LookupParameter('ADDS OCCUPANCY').AsInteger() == 1:
                spaces.append(sp)
        else:
            msg = 2
            spaces.append(sp)
    else:
        msg = 1
        spaces.append(sp)

if msg == 1:
    forms.alert("The 'ADDS OCCUPANCY' parameter does not exist in the Spaces category. "
            "For this tool, it will be assumed that all spaces DO add occupancy.", exitscript=False)
elif msg == 2:
    forms.alert("At least one space exists without the 'ADDS OCCUPANCY' parameter filled. "
            "It will be assumed these spaces DO add occupancy.", exitscript=False)


# 4️⃣ GET SPACE BOUNDARY LINES

# Get the bottom face of the spaces

spfacesinf = []
for sp in spaces:
    solid = list(sp.ClosedShell)[0]
    faces = list(solid.Faces)
    for face in faces:
        face_bb = [((face.GetBoundingBox().Min.U), (face.GetBoundingBox().Min.V)),
                   ((face.GetBoundingBox().Max.U), (face.GetBoundingBox().Max.V))]
        UV_mid = ((face_bb[0][0] + face_bb[1][0]) / 2, (face_bb[0][1] + face_bb[1][1]) / 2)
        face_n = face.ComputeNormal(UV(UV_mid[0], UV_mid[1]))
        if face_n.Z == -1:
            spfacesinf.append(face)

# Get boundary lines of the bottom faces and their p0 and p1 points

sp_edges_XYZ01 = []
for face in spfacesinf:
    edges = list(list(face.EdgeLoops)[0])
    edges_XYZ01 = []
    for e in edges:
        c = e.AsCurve()
        if "Line" in str(c.GetType()):
            XYZ01 = [c.GetEndPoint(0), c.GetEndPoint(1)]
            edges_XYZ01.append(XYZ01)
        else:
            XYZ01_0 = [c.Evaluate(0, True), c.Evaluate(0.33, True)]
            XYZ01_1 = [c.Evaluate(0.33, True), c.Evaluate(0.66, True)]
            XYZ01_2 = [c.Evaluate(0.66, True), c.Evaluate(1, True)]
            edges_XYZ01.append(XYZ01_0)
            edges_XYZ01.append(XYZ01_1)
            edges_XYZ01.append(XYZ01_2)
    sp_edges_XYZ01.append(edges_XYZ01)


# 5️⃣ INTERSECTION CALCULATION BETWEEN PATHS AND SPACES

# 1. FUNCTIONS

def ccw_XYZ(A, B, C):
    """Checks if points A, B, C are in counter-clockwise order"""
    return (C.Y - A.Y) * (B.X - A.X) > (B.Y - A.Y) * (C.X - A.X)

def intersect_XYZ(A, B, C, D):
    """Returns True if segments AB and CD intersect"""
    return (ccw_XYZ(A, C, D) != ccw_XYZ(B, C, D)) and (ccw_XYZ(A, B, C) != ccw_XYZ(A, B, D))

def ccw_xy(A, B, C):
    """Checks if points A, B, C are in counter-clockwise order (tuple version)"""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def intersect_xy(A, B, C, D):
    """Returns True if segments AB and CD intersect (tuple version)"""
    return (ccw_xy(A, C, D) != ccw_xy(B, C, D)) and (ccw_xy(A, B, C) != ccw_xy(A, B, D))

# 2. LOOPS

sp_with_intersection = []
sp_without_intersection = []
sp_without_intersection_edges_XYZ01 = []

for sp, spbound in zip(spaces, sp_edges_XYZ01):          # each space
    found = False
    for edge in spbound:                                 # each boundary line
        p0, p1 = edge
        for line in linpaths_XYZ01:                          # each path segment
            r0, r1 = line
            if intersect_XYZ(p0, p1, r0, r1):
                sp_with_intersection.append(sp)
                found = True
                break   # 1 intersection is enough
        if found:
            break

    # if NO intersection occurred, save the space and its edges
    if not found:
        sp_without_intersection.append(sp)
        sp_without_intersection_edges_XYZ01.append(spbound)


# 6️⃣ IDENTIFY SPACES WITH EVACUATION ORIGIN AT THEIR EXIT DOOR

# Get doors - works with curtain wall doors

all_doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
level_doors = [dr for dr in all_doors if dr.LevelId == stair_levelIN_id]


pathorgs = []
for path in paths:
    pathorgs.append((path.PathStart.X, path.PathStart.Y))

level_dorgs = []
for dr in level_doors:
    door_bb = dr.BoundingBox[doc.ActiveView]
    level_dorgs.append(((door_bb.Max.X + door_bb.Min.X) / 2, (door_bb.Max.Y + door_bb.Min.Y) / 2 ))

doors = []
doors_o = []
doors_n = []


for dr, dorg in zip(level_doors, level_dorgs):
    for pathorg in pathorgs:
        if distance_2d(dorg, pathorg) < 3:
            doors.append(dr)
            doors_o.append(dorg)
            doors_n.append((dr.FacingOrientation.X, dr.FacingOrientation.Y))
            break

# Get perpendicular line to the door

doors_p1p2 = []
k = 2
for o,n in zip(doors_o, doors_n):
    p1 = (o[0] + k * n[0], o[1] + k * n[1])
    p2 = (o[0] - k * n[0], o[1] - k * n[1])
    doors_p1p2.append([p1, p2])


# Search for intersection with previously discarded spaces

sp_with_door = []

for sp, spbound in zip(sp_without_intersection, sp_without_intersection_edges_XYZ01):
    found = False
    for edge in spbound:         # each boundary line
        p0, p1 = edge
        p0 = (p0.X, p0.Y)
        p1 = (p1.X, p1.Y)
        for line in doors_p1p2:    # each door perpendicular line
            r1, r2 = line
            if intersect_xy(p0, p1, r1, r2):
                sp_with_door.append(sp)
                found = True
                break  # 1 intersection is enough
        if found:
            break


# 7️⃣ COLLECT OCCUPANCY FROM DOORS / STAIRS + PREVIOUS STAIRS IN EVACUATION

# Collect people from doors where the parameter is filled

doors_wpeople = [dr for dr in doors if dr.LookupParameter('NUMBER PEOPLE').AsInteger() > 0]
people_doors = 0
for dr in doors_wpeople:
    people_doors = people_doors + dr.LookupParameter('NUMBER PEOPLE').AsInteger()


# Collect people from stairs + previous stairs in vertical evacuation

all_stairs = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()


all_stairs_levelOUT = []
all_stairs_pointOUT = []
msg = 0
for stair in all_stairs:
    if stair.LookupParameter('UPWARD EVACUATION') and stair.LookupParameter('UPWARD EVACUATION').StorageType == StorageType.Integer:
        if stair.LookupParameter('UPWARD EVACUATION').HasValue:
            stair_direction = stair.LookupParameter('UPWARD EVACUATION').AsInteger()
        else:
            msg = 1
            stair_direction = 0
    else:
        stair_direction = 0

    stair_levelBASE = stair.get_Parameter(BuiltInParameter.STAIRS_BASE_LEVEL_PARAM).AsValueString()
    stair_levelTOP = stair.get_Parameter(BuiltInParameter.STAIRS_TOP_LEVEL_PARAM).AsValueString()

    runs = list(stair.GetStairsRuns())
    runs_z = []
    for t in runs:
        t = doc.GetElement(t)
        runs_z.append(t.BaseElevation)
    runs_arranged = [x for _, x in sorted(zip(runs_z, runs))]

    runBASE_id = runs_arranged[0]
    runTOP_id = runs_arranged[-1]

    if stair_direction:
        stair_levelOUT = stair_levelTOP
        stair_runOUT = doc.GetElement(runTOP_id)
        stair_pointOUT = list(stair_runOUT.GetStairsPath())[-1].GetEndPoint(1)
    else:
        stair_levelOUT = stair_levelBASE
        stair_runOUT = doc.GetElement(runBASE_id)
        stair_pointOUT = list(stair_runOUT.GetStairsPath())[0].GetEndPoint(0)

    all_stairs_levelOUT.append(stair_levelOUT)
    all_stairs_pointOUT.append(stair_pointOUT)

if msg == 1:
    forms.alert("At least one stair in the project is missing the 'UPWARD EVACUATION' parameter. "
                "For this tool, these stairs will be assumed as DOWNWARD evacuation.", exitscript=False)

# Filter stairs that discharge at the current level
stairs_level = []
pointsOUT_level = []
for stair, lvl, pt in zip(all_stairs, all_stairs_levelOUT, all_stairs_pointOUT):
    if lvl == stair_levelIN:
        stairs_level.append(stair)
        pointsOUT_level.append(pt)

# Spatial check to see if the discharging stair belongs to the current evacuation path
stairs = []
for stair, pt in zip(stairs_level, pointsOUT_level):
    bb_max = (stair.BoundingBox[doc.ActiveView].Max.X, stair.BoundingBox[doc.ActiveView].Max.Y)
    bb_min = (stair.BoundingBox[doc.ActiveView].Min.X, stair.BoundingBox[doc.ActiveView].Min.Y)
    x, y = stair_bb_med

    # VERTICAL CONTINUITY
    # Check if the mid-point of the evacuation stair's Bounding Box is inside the current stair's BB
    INbb = (bb_min[0] <= x <= bb_max[0]) and (bb_min[1] <= y <= bb_max[1])

    # Check if the distance between the IN point and OUT point is within tolerance (5 feet)
    if INbb or distance_2d((pointIN.X, pointIN.Y), (pt.X, pt.Y)) < 5:
        stairs.append(stair)

    # STAIRS FROM PATH ORIGIN
    else:
        for path in paths:
            if distance_2d((path.PathStart.X, path.PathStart.Y), (pt.X, pt.Y)) < 3:
                stairs.append(stair)
                break

people_stairs = 0
for stair in stairs:
    people_stairs = people_stairs + stair.LookupParameter('NUMBER PEOPLE').AsInteger()


# 8️⃣ GROUP ALL SPACES, SUM THEIR OCCUPANCY, AND ADD PEOPLE FROM DOORS AND STAIRS

evac_spaces = list(set(sp_with_intersection + sp_with_door))


def parse_asvaluestring_to_int(value_str):
    """
    Converts a Revit AsValueString (with commas, dots, units, etc.)
    to an integer rounded up.
    """
    if not value_str:
        return None

    # 1. Remove everything that isn't a digit, dot, or comma
    clean = re.sub(r"[^0-9,.\-]", "", value_str)

    # 2. Unify format: if there is a decimal comma → change to dot
    if "," in clean and "." not in clean:
        clean = clean.replace(",", ".")

    # 3. Convert to float
    try:
        num = float(clean)
    except ValueError:
        return None

    # 4. Round up and return integer
    return int(math.ceil(num))


number_people = 0
for sp in evac_spaces:
    people_str = sp.get_Parameter(BuiltInParameter.ROOM_NUMBER_OF_PEOPLE_PARAM).AsValueString()
    people_int = parse_asvaluestring_to_int(people_str)
    number_people = number_people + people_int

number_people = number_people + people_doors + people_stairs


# 9️⃣ FILL STAIR PARAMETERS

min_width = max(number_people / 160.0, 1.0)        # CHECK
min_width_ft = min_width * 3.28084

t = Transaction(doc, __title__)
t.Start()

stair_NP = stair.LookupParameter('NUMBER PEOPLE')
stair_NP.Set(number_people)

stair_MW = stair.LookupParameter('MINIMUM WIDTH')
stair_MW.Set(min_width_ft)

t.Commit()

# 🔟 FINAL MESSAGE: COMPLIANT / NON-COMPLIANT

# Get stair width

total_width = runOUT.ActualRunWidth
total_width_m = total_width / 3.28084
w = total_width + 0.09999

if w >= min_width_ft:
    forms.alert(
        "Calculated occupancy: {}. This requires a minimum stair width of {:.2f} m according to CTE DB-SI (assuming unprotected downward stairs).\n\n"
        "These values have been added to the 'NUMBER PEOPLE' and 'MINIMUM WIDTH' parameters.\n\n"
        
        "The current stair width is {:.2f} m: PASSES the minimum evacuation width requirement."
        .format(number_people, float(min_width), float(total_width_m)), exitscript=False)

else:
    forms.alert(
        "Calculated occupancy: {}. This requires a minimum stair width of {:.2f} m according to CTE DB-SI (assuming unprotected downward stairs).\n\n"
        "These values have been added to the 'NUMBER PEOPLE' and 'MINIMUM WIDTH' parameters.\n\n"

        "The current stair width is {:.2f} m: DOES NOT COMPLY with the minimum evacuation width requirement."
        .format(number_people, float(min_width), float(total_width_m)), exitscript=False)
