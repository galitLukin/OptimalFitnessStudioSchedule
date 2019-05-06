import pandas as pd
import numpy as np

import cleaning

D = 7
T = 28
C = 8
I = 18

def findCategory(dt,ci,categories):
    for index, row in categories.iterrows():
        if dt in row.DT and ci in row.CI:
            return index
    return

attendance = pd.read_csv('../Data/predict/attendanceGrouped.csv')
categories = pd.read_csv('../Data/predict/categories.csv')

#filter old instructors
attendance.Staff = attendance.Staff.apply(lambda instructor: cleaning.filterInstructors(instructor))
attendance = attendance.loc[attendance.Staff != "Filter"]

attendance.columns = ['Date', 'StartTime', 'Description', 'Staff', 'ClientID']
attendance['Date'] = pd.to_datetime(attendance['Date'])
attendance['StartTime'] = pd.to_datetime(attendance['StartTime'])
attendance['WeekDay'] = attendance.Date.apply(lambda x: x.strftime("%A"))

attendance.Staff = attendance.Staff.apply(lambda x : cleaning.instructors.index(x) + 1)
attendance.Description = attendance.Description.apply(lambda x : cleaning.classes.index(x) + 1)
attendance.WeekDay = attendance.WeekDay.apply(lambda x : cleaning.weekDays.index(x) + 1)
attendance.StartTime = attendance.StartTime.apply(lambda x : int(((x.hour + x.minute/60.0) - 6)*2+1))

gr = attendance.groupby(pd.Grouper(key='Date',freq='W-MON'))
weekDate = pd.DataFrame(columns= ['Week'])
for name,group in gr:
    dates = group.loc[:,'Date'].unique()
    for d in dates:
        weekDate.loc[d,'Week'] = name.date()
weekDate.index.name = 'Date'
weekDate = weekDate.reset_index()

attendance = pd.merge(attendance,weekDate, on = 'Date', how = 'inner')

#print(attendance)

data = pd.DataFrame(0, index = range(1,32), columns = ["Cat{}".format(i) for i in range(1,5)])

gr = attendance.groupby(pd.Grouper(key='Week'))

weeklyArrivals = []
i,j = 0,0
w = 1
for name, group in gr:
    categoryDict = {}
    for index, row in group.iterrows():
        dt = "D_{}_T_{}".format(row.WeekDay,row.StartTime)
        ci = "C_{}_I_{}".format(row.Description,row.Staff)
        #implement this function
        cat = findCategory(dt,ci,categories)
        if cat:
            j = j + 1
            if cat in categoryDict.keys():
                categoryDict[cat] = categoryDict[cat] + row.ClientID
            else:
                categoryDict[cat] = row.ClientID
        else:
            i = i + 1
    for c,arrivals in categoryDict.items():
        data.loc[w,"Cat{}".format(c)] = arrivals
    w = w + 1
print(j,i)
#print(list(data))
print(data)
