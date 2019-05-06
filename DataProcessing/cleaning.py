import pandas as pd
import datetime
from datetime import datetime as dt

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


def removeOutlierWeeks(perDate):
    demand = perDate['Client ID'].tolist()
    plt.hist(demand, bins=10)
    plt.title("Histogram of Demand")
    plt.show()
    perDate['Date'] = pd.to_datetime(perDate['Date'])
    gr = perDate.groupby(pd.Grouper(key='Date',freq='W-MON'))
    weeks = []
    weekDemand = []
    first = datetime.date(2018,10,7)
    first = '2018-10-01 00:00:00'
    first = datetime.datetime.strptime(first, '%Y-%m-%d %H:%M:%S')
    christmas1 = '2018-12-24 00:00:00'
    christmas1 = datetime.datetime.strptime(christmas1, '%Y-%m-%d %H:%M:%S')
    christmas2 = '2018-12-31 00:00:00'
    christmas2 = datetime.datetime.strptime(christmas2, '%Y-%m-%d %H:%M:%S')
    for name, group in gr:
        #remove first week of studio and last week of 2018 due to christmas
        if name == first or name == christmas1 or name == christmas2:
            for index, row in group.iterrows():
                perDate = perDate.loc[perDate['Date'] != row['Date']]
        else:
            weeks.append(name)
            weekDemand.append(sum(group['Client ID'].tolist()))
    plt.bar(weeks, weekDemand, align='center', alpha=0.5)
    d = {'Week' : weeks, 'Arrivals' : weekDemand}
    WEEK = pd.DataFrame(data=d)
    WEEK.to_csv('../Data/processed/WEEKdemand.csv', index = False)
    plt.show()
    return perDate


def timeSlots():
    start = '06:00:00'
    prev = datetime.datetime.strptime(start, '%H:%M:%S')
    times = [(prev.hour, prev.minute)]
    for i in range(1,29):
        t = prev + datetime.timedelta(minutes=30)
        times.append((t.hour, t.minute))
        prev = t
    return times


def fillTimeSlots(u,T):
    #Fill in missing timeSlots
    pastSlots = T.StartTime_.tolist()
    pastMax = T.Arrivals_q4.tolist()
    pastMin = T.Arrivals_q2.tolist()
    for i in range(1,29):
        if i in pastSlots:
            ind = pastSlots.index(i)
            u.at['Time{}'.format(i),:] = [pastMin[ind], pastMax[ind]]
            continue
        prev, next = 1, 1
        while i - prev not in pastSlots:
            prev = prev + 1
        ind = pastSlots.index(i - prev)
        prev = pastSlots[ind]
        prevMax = pastMax[ind]
        prevMin = pastMin[ind]
        while i + next not in pastSlots and i+next<=28:
            next = next + 1
        if i + next < 28:
            ind = pastSlots.index(i + next)
            next = pastSlots[ind]
            nextMax = pastMax[ind]
            nextMin = pastMin[ind]
            ma = ( prev * nextMax + next * prevMax ) / ( prev + next )
            mi = ( prev * nextMin + next * prevMin ) / ( prev + next )
        else:
            mi = prevMin
            ma = prevMax
        u.at['Time{}'.format(i),:] = [mi, ma]
    return u
