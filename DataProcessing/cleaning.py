import pandas as pd

classDataMap = {
    "HOT 26" : ["HOT 26", "HOT 26 + BACKBENDS", "HOT 26 FLOW", "HOT 26+", "CLASSIC 90", "EXPRESS 60", "SILENT HOT 26", "SILENT 90", "SILENT 60"],
    "INFERNO HOT PILATES" : ["INFERNO HOT PILATES", "INFERNO HOT PILATES LEVEL II", "CHARITY INFERNO HOT PILATES"],
    "HOT HATHA FUSION" : ["HOT HATHA FUSION"],
    "HOT HATHA SCULPT" : ["HOT HATHA SCULPT"]
}

classes = ["HOT 26", "HOT 26 FLOW", "SILENT HOT 26", "HOT 26+", "INFERNO HOT PILATES", "INFERNO HOT PILATES LEVEL II", "HOT HATHA FUSION", "HOT HATHA SCULPT"]
instructors = ["ANCIVAL, SOPHIE", "BOU-NASSIF, JASMINE", "BOUJOULIAN, RACHELLE", "CATES, SHELLEY", "EVANGELISTI, MEREDITH", "HEIRTZLER, LESLIE", "JONES, JACLYN", "LAMBERT, LUCAS", "LANSING, LUCAS", "LOVERME, KYLA", "MCGRATH, SHARON", "MONROE, KYLAH", "PHAN, STEVEN", "PIGOTT, ELLEN", "SERRANO, JIMMY", "STERN, BRIAN", "VEERAPEN, KUMAR", "WOODS, TESS"]


def currectClasses(c):
    if c in classDataMap.keys():
        return c
    else:
        for key,val in classDataMap.items():
            if c in val:
                return key
    return "Filter"

def filterInstructors(instructor):
    if instructor in instructors:
        return instructor
    return "Filter"
