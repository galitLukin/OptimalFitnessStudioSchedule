import pandas as pd
import datetime
from datetime import datetime as dt
import glob
import matplotlib.pyplot as plt

classDataMapOld = {
    "HOT26" : ["HOT26", "HOT26+BACKBENDS", "HOT26FLOW", "HOT26+", "CLASSIC90", "EXPRESS60", "SILENTHOT26", "SILENT90", "SILENT60"],
    "INFERNOHOTPILATES" : ["INFERNOHOTPILATES", "INFERNOHOTPILATESLEVELII", "CHARITYINFERNOHOTPILATES"],
    "HOTHATHAFUSION" : ["HOTHATHAFUSION"],
    "HOTHATHASCULPT" : ["HOTHATHASCULPT"]
}

classDataMap = {
    "HOT26" : ["HOT26", "HOT26+BACKBENDS", "CLASSIC90", "EXPRESS60", "SILENT90", "SILENT60"],
    "INFERNOHOTPILATES" : ["INFERNOHOTPILATES", "CHARITYINFERNOHOTPILATES"],
    "HOTHATHAFUSION" : ["HOTHATHAFUSION"],
    "HOTHATHASCULPT" : ["HOTHATHASCULPT"],
    "HOT26FLOW" : ["HOT26FLOW"],
    "HOT26+" : ["HOT26+"],
    "SILENTHOT26" : ["SILENTHOT26"],
    "INFERNOHOTPILATESLEVELII" : ["INFERNOHOTPILATESLEVELII"]
}

classes = ["HOT26", "HOT26FLOW", "SILENTHOT26", "HOT26+", "INFERNOHOTPILATES", "INFERNOHOTPILATESLEVELII", "HOTHATHAFUSION", "HOTHATHASCULPT"]
instructors = ["ANCIVAL,SOPHIE", "BOU-NASSIF,JASMINE", "BOUJOULIAN,RACHELLE", "CATES,SHELLEY", "EVANGELISTI,MEREDITH", "HEIRTZLER,LESLIE", "JONES,JACLYN", "LAMBERT,LUCAS", "LANSING,LUCAS", "LOVERME,KYLA", "MCGRATH,SHARON", "MONROE,KYLAH", "PHAN,STEVEN", "PIGOTT,ELLEN", "SERRANO,JIMMY", "STERN,BRIAN", "VEERAPEN,KUMAR", "WOODS,TESS"]
weekDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def stripSpaces(df):
    df['Description'] = df['Description'].str.replace(" ","")
    df['Staff'] = df['Staff'].str.replace(", ",",")
    return df


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

def timeSlots():
    start = '06:00:00'
    prev = datetime.datetime.strptime(start, '%H:%M:%S')
    times = [(prev.hour, prev.minute)]
    for i in range(1,29):
        t = prev + datetime.timedelta(minutes=30)
        times.append((t.hour, t.minute))
        prev = t
    return times

def fillTimeSlots(dt, d, t):
    day = dt.loc[dt.WeekDay == d]
    pastSlots = day.StartTime.tolist()
    arrivals = day.avgArrivals.tolist()
    prev, next = 1, 1
    while t - prev not in pastSlots and t - prev >= 0:
        prev = prev + 1
    while t + next not in pastSlots and t + next <= 29:
        next = next + 1
    if t - prev <= 0 and t + next >= 29:
        return 0
    elif t - prev <= 0 and t + next < 29:
        ind = pastSlots.index(t + next)
        return arrivals[ind]
    elif t - prev > 0 and t + next >= 29:
        ind = pastSlots.index(t - prev)
        return arrivals[ind]
    else:
        pind = pastSlots.index(t - prev)
        nind = pastSlots.index(t + next)
        nextArrivals = arrivals[nind]
        prevArriavls = arrivals[pind]
        return ( prev * nextArrivals + next * prevArriavls ) / ( prev + next )
    return u


def filterandGroup():
        attendanceList = []
        files = glob.glob('../Data/raw/' + "/*.xlsx")

        for f in files:
            temp = pd.read_excel(f)
            temp = temp.loc[:,['Date', 'Start time', 'Description', 'Staff', 'Client ID', 'Status']]
            attendanceList.append(temp)

        attendance = pd.concat(attendanceList)
        attendance = stripSpaces(attendance)

        #take only users that arrived
        attendance = attendance.loc[(attendance['Status'] == 'Signed in') | (attendance['Status'] == 'Reserved')]
        attendance = attendance.loc[:,['Date', 'Start time', 'Description', 'Staff', 'Client ID']]

        #filter old instructors
        attendance.Staff = attendance.Staff.apply(lambda instructor: filterInstructors(instructor))
        attendance = attendance.loc[attendance.Staff != "Filter"]

        #attendance per day per class
        perDate = attendance.loc[:,['Date','Start time','Client ID']]
        perDate = perDate.groupby(['Date','Start time']).count().reset_index()
        perDate = perDate.groupby('Date').sum().reset_index()

        #take only relevant dates
        allDates = perDate.loc[:,'Date'].to_frame()
        attendance = pd.merge(attendance, allDates, on = 'Date', how = 'inner')

        #map classes and filter those that don't match
        attendance.Description = attendance.Description.apply(lambda c: currectClasses(c))
        attendance = attendance.loc[attendance.Description != "Filter"]

        # group clients per class
        attendance = attendance.groupby(['Date','Start time','Description','Staff']).count().reset_index()
        attendance.to_csv('../Data/output/attendanceGrouped.csv', index = False)
        return attendance
