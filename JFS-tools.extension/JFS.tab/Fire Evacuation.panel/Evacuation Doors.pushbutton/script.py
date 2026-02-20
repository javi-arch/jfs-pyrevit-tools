# -*- coding: utf-8 -*-
__title__   = "Evacuation Doors"
__doc__     = """Version = 1.1
Date     = 05.09.2025
________________________________________________________________
Description:

EN - This tool calculates the number of people for which a floor or building evacuation door must be dimensioned, automatically filling in its 'MINIMUM WIDTH' and 'NUMBER PEOPLE' parameters.
ES - Esta herramienta calcula el número de personas para las que debe ser dimensionada una puerta de evacuación de planta o edificio rellenando automáticamente sus parámetros de 'MINIMUM WIDTH' y 'NUMBER PEOPLE'.
________________________________________________________________
How-To:

EN - The tool collects the occupancy of spaces through which evacuation paths pass that culminate (path end) at the door selected by the user.
Paths may originate at an exit door of a space if permitted by regulations; the tool will detect the occupancy of this space regardless.
The tool also collects the number of people evacuated from stairs or doors found at the origin of the evacuation paths.

ES - La herramienta recoge las ocupaciones de los espacios por los que pasan las paths  que culminan (fin de la path) en la puerta seleccionada por el usuario.
Las paths pueden tener su origen en una puerta de salida de un espacio si así se permite por normativa, la herramienta detectará la ocupación de este espacio igualmente.
La herramienta también recoge el número de personas evacuadas desde stairs o puertas que encuentre en el origen de las paths de evacuación.
________________________________________________________________
TODO:

- New functionalities as they arise. Currently, the tool is complete.
________________________________________________________________
Last Updates:

- [28.08.2025] v1.0 Initial version without detection of people evacuated from stairs or doors at the evacuation origin.
- [05.09.2025] v1.1 Tool complete.
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

res = forms.alert("EN - This tool calculates the number of people for which a floor/building evacuation door must be dimensioned by automatically filling in its 'MINIMUM WIDTH' and 'NUMBER PEOPLE' parameters. Before continuing, consider the following conditions for correct operation:\n\n"

"- Shared parameters 'MINIMUM WIDTH' (Data type: Length) and 'NUMBER PEOPLE' (Data type: Integer) must be created in the 'Common' discipline for the Door and Stairs categories.\n\n"

"- All evacuation paths (Path of Travel lines) for the floor must be drawn, and spaces (review the 'ADDS OCCUPANCY' parameter) must have their occupancy correctly assigned. The tool collects occupancies from spaces where paths culminate at the analyzed door. Paths can originate at a space exit door if allowed by code; the tool will detect the occupancy correctly.\n\n"

"- Paths and corresponding spaces must be associated with the same level as the analyzed door. For example, if paths and spaces are on 'Level 1' but the door is associated with 'Level 1_Terrace', the tool will fail. The door level must match the path/space level regardless of offsets.\n\n"

"- The tool also collects the ‘NUMBER PEOPLE’ from doors and stairs from which evacuation routes originate to the exit door. To calculate the ‘NUMBER PEOPLE’ for stairs, it is recommended to use the 'Evacuation Stairs' tool. For these tools to work correctly in projects with upward evacuation stairs, it is essential to use the shared parameter ‘UPWARD EVACUATION’ (Data Type: Yes/No) in the ‘Common’ discipline, for the stairs category. It is important to consider cases in which the origin of the route does not reach the stair, but where regulations allow it to start at a prior compartment (protected stairs, for example). In these cases, the correct approach is to use the 'Evacuation Stairs' tool and then manually transfer the calculated ‘NUMBER PEOPLE’ to the compartment door parameter, which will be taken into account when running the protocol tools.\n\n\n"

"ES - Esta herramienta calcula el número de personas para las que debe ser dimensionada una puerta de evacuación de planta o edificio rellenando automáticamente sus parámetros de 'MINIMUM WIDTH' y 'NUMBER PEOPLE'. Antes de continuar ten en cuenta las siguientes condiciones para su correcto funcionamiento:\n\n"

"- Deben estar creados los parámetros compartidos 'MINIMUM WIDTH' (Tipo de dato: Longitud) y 'NUMBER PEOPLE' (Tipo de dato: Entero) en disciplina 'Común', para las categorías de puertas y stairs.\n\n"

"- Todas las paths de evacuación (Líneas de camino del recorrido) de la planta deben estar dibujadas, así como los espacios (revisar parámetro 'ADDS OCCUPANCY'), que deben tener su ocupación corlinemente asignada: la herramienta recoge las ocupaciones de los espacios por los que pasan las paths que culminan (fin de la path) en la puerta a analizar. Las paths pueden tener su origen en una puerta de salida de un espacio si así se permite por normativa, la herramienta detectará la ocupación de este espacio igualmente.\n\n"

"- Las paths (Líneas de camino del recorrido) y espacios correspondientes deben estar asociados al mismo nivel que la puerta de evacuación a analizar. Por ejemplo, si paths y espacios están construidos en el nivel 'Level 1', pero la puerta de evacuación está asociada al nivel 'Level 1_Terrace', la herramienta fallará. En este ejemplo el nivel de la puerta debe ser 'P01', independientemente del desfase o 'Altura de antepecho' que pueda tener.\n\n"

"- La herramienta también recoge el 'NUMBER PEOPLE' de puertas y stairs desde las que parten paths de evacuación hasta la puerta. Para calcular el 'NUMBER PEOPLE' de stairs se recomienda utilizar la herramienta 'Evacuation Stairs'. Para que estas herramientas funcionen corlinemente en proyectos con stairs de evacuación ascendente es imprescindible utilizar el parámetro compartido 'UPWARD EVACUATION' (Tipo de dato: Sí/No) en disciplina 'Común', "
"para la categoría de stairs. Es importante tener en cuenta casos en los que el origen de la path no llega a la escalera, sino que por normativa es suficiente con que empieze en una compartimentación previa (stairs protegidas, por ejemplo). En estos casos lo correcto es usar la herramienta 'Evacuation Stairs' para después pasar manualmente el 'NUMBER PEOPLE' calculado al parámetro de la puerta de la compartimentación, el cual será tenido en cuenta al ejecutar las herramientas del protocolo."
"\n\n",

options=["Cancel", "Select door"])

if res == "Cancel":
    sys.exit()


# 1️⃣ SELECT DOOR TO ANALYZE AND GET ITS LEVEL AND LOCATION

# Filter to make only elements from the "Doors" category selectable:

class door_filter(ISelectionFilter):
    def AllowElement(self, elem):
        if elem.Category.BuiltInCategory == BuiltInCategory.OST_Doors:
            return True
try:
    sel_door = uidoc.Selection.PickObject(ObjectType.Element, door_filter())
    door = doc.GetElement(sel_door)
except:
    forms.alert('Nothing selected. Please select an evacuation door to continue.', exitscript=True)

# Parameter check

if not door.LookupParameter('NUMBER PEOPLE'):
    forms.alert("The parameter 'NUMBER PEOPLE' does not exist in the Doors category. "
            "Add this shared parameter for the tool to function correctly.", exitscript=True)

if not door.LookupParameter('MINIMUM WIDTH'):
    forms.alert("The parameter 'MINIMUM WIDTH' does not exist in the Doors category. "
            "Add this shared parameter for the tool to function correctly.", exitscript=True)

door_levelid    = door.LevelId
door_level      = doc.GetElement(door_levelid).Name

#door_loc       = door.Location.Point      # Not valid for curtain wall doors

door_bb         = door.BoundingBox[doc.ActiveView]
door_loc        = ((door_bb.Max.X + door_bb.Min.X)/2, (door_bb.Max.Y + door_bb.Min.Y)/2)


# 2️⃣ FIND EVACUATION PATHS THAT END AT THE ANALYZED DOOR AND GET THEIR COMPONENT LINES

# # Get evacuation paths for this level

all_paths = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PathOfTravelLines).WhereElementIsNotElementType().ToElements()
level_paths = [path for path in all_paths if path.get_Parameter(BuiltInParameter.PATH_OF_TRAVEL_LEVEL_NAME).AsString() == door_level]

# Keep only those that end at the evacuation door (PathEnd within 3ft (90cm) of the door location)

paths = [path for path in level_paths if distance_2d((path.PathEnd.X,path.PathEnd.Y),door_loc) < 3]

if not paths:
    forms.alert('No evacuation path ends at the selected door. You must draw the evacuation paths for the floor/building before running this tool.', exitscript=True)

# Get a list of all lines that compose the paths (flattened)

linpaths = []
for path in paths:
    lines = list(path.GetCurves())
    for line in lines:
        linpaths.append(line)

# Get p0 and p1 (start/end points) of the lines

linpaths_XYZ01 = []
for line in linpaths:
    XYZ01 = [line.GetEndPoint(0), line.GetEndPoint(1)]
    linpaths_XYZ01.append(XYZ01)


# 3️⃣ COLLECT SPACES WITH LEVEL FILTERS AND 'ADDS OCCUPANCY'

all_spaces = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MEPSpaces).WhereElementIsNotElementType().ToElements()
level_spaces = [sp for sp in all_spaces if sp.LevelId == door_levelid]

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
    forms.alert("The parameter 'ADDS OCCUPANCY' does not exist in the Spaces category. For the purposes of this tool, it will be assumed that all spaces DO add occupancy.", exitscript=False)
elif msg == 2:
    forms.alert("There is at least one space without the 'ADDS OCCUPANCY' parameter filled. For the purposes of this tool, it will be assumed that these spaces DO add occupancy.", exitscript=False)


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
level_doors = [dr for dr in all_doors if dr.LevelId == door_levelid]


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

if not sp_with_intersection:
    doors.append(door)
    # Add the evacuation door to this 'doors' list to include the space if it's unique and doesn't intersect with any path
    doors_o.append(door_loc)
    doors_n.append((door.FacingOrientation.X, door.FacingOrientation.Y))

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


# 7️⃣ COLLECT OCCUPANCY FROM DOORS / STAIRS

# Collect people from doors with the parameter filled

if door in doors:
    doors.remove(door)

doors_wpeople = [dr for dr in doors if dr.LookupParameter('NUMBER PEOPLE').AsInteger() > 0]
people_doors = 0
for dr in doors_wpeople:
    people_doors = people_doors + dr.LookupParameter('NUMBER PEOPLE').AsInteger()

# Collect people from stairs

all_stairs = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()

all_stairs_levelOUT = []
all_stairs_pointOUT = []
msg = 0
for stair in all_stairs:
    if stair.LookupParameter('UPWARD EVACUATION') and stair.LookupParameter('UPWARD EVACUATION').StorageType == StorageType.Integer:
        if stair.LookupParameter('UPWARD EVACUATION').HasValue:
            stair_direction = stair.LookupParameter('UPWARD EVACUATION').AsInteger()
        else:
            msg = 2
            stair_direction = 0
    else:
        msg = 1
        stair_direction = 0

    stair_levelBASE = stair.get_Parameter(BuiltInParameter.STAIRS_BASE_LEVEL_PARAM).AsValueString()
    stair_levelTOP = stair.get_Parameter(BuiltInParameter.STAIRS_TOP_LEVEL_PARAM).AsValueString()

    runs = list(stair.GetStairsRuns())
    runs_z = []
    for r in runs:
        r = doc.GetElement(r)
        runs_z.append(r.BaseElevation)
    runs_arranged = [x for _, x in sorted(zip(runs_z, runs))]

    runBASE_id = runs_arranged[0]
    runTOP_id = runs_arranged[-1]

    if stair_direction:
        stair_levelOUT = stair_levelTOP
        runOUT = doc.GetElement(runTOP_id)
        pointOUT = list(runOUT.GetStairsPath())[-1].GetEndPoint(1)
    else:
        stair_levelOUT = stair_levelBASE
        runOUT = doc.GetElement(runBASE_id)
        pointOUT = list(runOUT.GetStairsPath())[0].GetEndPoint(0)

    all_stairs_levelOUT.append(stair_levelOUT)
    all_stairs_pointOUT.append(pointOUT)

if msg == 1:
    forms.alert("The parameter 'UPWARD EVACUATION' does not exist in the Stairs category. "
                "For the purposes of this tool, all stairs will be assumed to be DOWNWARD evacuation.\n\n"
                "Add this shared parameter for the tool to function correctly if upward evacuation "
                "stairs exist.", exitscript=False)
elif msg == 2:
    forms.alert("There is at least one staircase without the 'UPWARD EVACUATION' parameter filled. For the purposes of this tool, these will be assumed as DOWNWARD evacuation.", exitscript=False)

stairs_level = []
pointsOUT_level = []
for stair, lvl, pt in zip(all_stairs, all_stairs_levelOUT, all_stairs_pointOUT):
    if lvl == door_level:
        stairs_level.append(stair)
        pointsOUT_level.append(pt)

stairs = []
for stair, pt in zip(stairs_level, pointsOUT_level):
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


# 9️⃣ FILL DOOR PARAMETERS

min_width = max(number_people/200.0, 0.80)
min_width_ft = min_width * 3.28084

t = Transaction(doc, __title__)
t.Start()

door_NP = door.LookupParameter('NUMBER PEOPLE')
door_NP.Set(number_people)

door_MW = door.LookupParameter('MINIMUM WIDTH')
door_MW.Set(min_width_ft)

t.Commit()

# 🔟 FINAL MESSAGE: COMPLIANT / NON-COMPLIANT

# Get door width / curtain wall door width

# CW ...
total_width = door.get_Parameter(BuiltInParameter.FURNITURE_WIDTH).AsDouble()

# Not CW ...
if total_width == 0:
    door_typeid = door.GetTypeId()
    total_width = doc.GetElement(door_typeid).get_Parameter(BuiltInParameter.FURNITURE_WIDTH).AsDouble()

total_width_m = total_width / 3.28084
w = total_width + 0.09999
# Tolerance for unit conversion inaccuracies (prevents false non-compliance)


if w >= min_width_ft:
    forms.alert(
        "The calculated number of people is {}, which requires a minimum door width of {:.2f} m according to CTE DB-SI.\n\n"
        "These values have been added to the 'NUMBER PEOPLE' and 'MINIMUM WIDTH' parameters respectively.\n\n"
    
        "The current total width of the door is {:.2f} m, so it IS COMPLIANT with the minimum evacuation width."
        .format(number_people, float(min_width), float(total_width_m)), exitscript=False)

else:
    forms.alert(
        "The calculated number of people is {}, which requires a minimum door width of {:.2f} m according to CTE DB-SI.\n\n"
        "These values have been added to the 'NUMBER PEOPLE' and 'MINIMUM WIDTH' parameters respectively.\n\n"

        "The current total width of the door is {:.2f} m, so it IS NOT COMPLIANT with the minimum evacuation width."
        .format(number_people, float(min_width), float(total_width_m)), exitscript=False)