import pandas as pd
import glob
import datetime
import matplotlib.pyplot as plt
import numpy as np

import cleaning

attendanceList = []
files = glob.glob('../Data/raw/' + "/*.xlsx")

for f in files:
    temp = pd.read_excel(f)
    temp = temp.loc[:,['Date', 'Start time', 'Description', 'Staff', 'Client ID', 'Status']]
    attendanceList.append(temp)

attendance = pd.concat(attendanceList)
attendance = cleaning.stripSpaces(attendance)

#take only users that arrived
attendance = attendance.loc[(attendance['Status'] == 'Signed in') | (attendance['Status'] == 'Reserved')]
attendance = attendance.loc[:,['Date', 'Start time', 'Description', 'Staff', 'Client ID']]

#attendance per day per class
perDate = attendance.loc[:,['Date','Start time','Client ID']]
perDate = perDate.groupby(['Date','Start time']).count().reset_index()
perDate = perDate.groupby('Date').sum().reset_index()

#take only relevant dates
allDates = perDate.loc[:,'Date'].to_frame()
attendance = pd.merge(attendance, allDates, on = 'Date', how = 'inner')

#map classes and filter those that don't match
attendance.Description = attendance.Description.apply(lambda c: cleaning.currectClasses(c))
attendance = attendance.loc[attendance.Description != "Filter"]

# group clients per class
attendance = attendance.groupby(['Date','Start time','Description','Staff']).count().reset_index()
attendance.to_csv('../Data/predict/attendanceGrouped.csv', index = False)

attendance['Date'] = pd.to_datetime(attendance['Date'])
attendance['WeekDay'] = attendance.Date.apply(lambda x: x.strftime("%A"))
dailyArrivals = attendance.groupby(['Date'])['Client ID'].sum().reset_index()
gr = dailyArrivals.groupby(pd.Grouper(key='Date',freq='W-MON'))
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
perDay = pd.DataFrame(index = days, columns = ['Arrivals'])
weeklyArrivals = pd.DataFrame(columns = ['DateWeek','Date','WeekArrivals'])
for d_ in days:
    perDay.loc[d_,'Arrivals'] = []
for name, group in gr:
    weeklyA = sum(group['Client ID'].tolist())
    for index, row in group.iterrows():
        weeklyArrivals.loc[index,'DateWeek'] = name
        weeklyArrivals.loc[index,'Date'] = row.Date.date()
        weeklyArrivals.loc[index,'WeekArrivals'] = weeklyA
    group.loc[:,'WeekDay'] = group.Date.apply(lambda x: x.strftime("%A"))
    for d_ in days:
        temp = group.loc[group.WeekDay == d_]
        temp = temp.reset_index(drop=True)
        if temp.empty:
            perDay.loc[d_,'Arrivals'].append(0)
        else:
            perDay.loc[d_,'Arrivals'].append(float(temp.loc[:,'Client ID'][0])/weeklyA)

perDay.to_csv('../Data/predict/perDay.csv', index = False)

weeklyArrivals['Date'] = pd.to_datetime(weeklyArrivals['Date'])
perTime = pd.merge(weeklyArrivals, attendance, on = 'Date', how = 'inner')
perTime['DayTimePopularity'] = perTime.apply(lambda x: float(x['Client ID'])/x.WeekArrivals, axis = 1)
perTime = perTime.loc[:,['WeekDay','Start time', 'DayTimePopularity']]
perTime = perTime.groupby(['WeekDay','Start time'])['DayTimePopularity'].apply(list).reset_index()
perTime.to_csv('../Data/predict/perTime.csv', index = False)

dt = pd.DataFrame(columns = ['MeanArrivals','StdArrivals'])

for i in range(7):
    day = perTime.loc[perTime.WeekDay == days[i]]
    times = day['Start time'].tolist()
    for t in times:
        allt = day.loc[perTime['Start time'] == t]
        temp = []
        for index, row in allt.iterrows():
            temp = temp + row.DayTimePopularity
        x = np.array([t.hour + t.minute/60.0] * len(temp))
        y = np.array(temp)
        dt.loc['D_{}_T_{}'.format(i+1,int(((t.hour + t.minute/60.0) - 6)*2+1)),:] = [np.mean(y),np.std(y)]
        #plt.scatter(x,y)
    #plt.show()

bestDT = dt.loc[dt.MeanArrivals >= 0.03]
#medDT = dt.loc[(dt.MeanArrivals < 0.04) & (dt.MeanArrivals >= 0.02)]
worstDT = dt.loc[dt.MeanArrivals < 0.03]
bestDT = bestDT.index.tolist()
#medDT = medDT.index.tolist()
worstDT = worstDT.index.tolist()

ciArrivals = attendance.groupby(['Date','Description','Staff'])['Client ID'].sum().reset_index()
perCI = pd.merge(weeklyArrivals, ciArrivals, on = 'Date', how = 'inner')
perCI = perCI.groupby(['DateWeek','Description','Staff','WeekArrivals'])['Client ID'].sum().reset_index()
ci = pd.DataFrame(columns = ['MeanArrivals','StdArrivals'])
for c in cleaning.classes:
    for i in cleaning.instructors:
        tempdf = perCI.loc[(perCI.Description == c) & (perCI.Staff == i)]
        if tempdf.empty:
            continue
        y = []
        for index, row in tempdf.iterrows():
            y.append(float(row['Client ID'])/row.WeekArrivals)
        indc = cleaning.classes.index(row.Description)
        indi = cleaning.instructors.index(row.Staff)
        ci.loc['C_{}_I_{}'.format(indc,indi),:] = [np.mean(y),np.std(y)]

bestCI = ci.loc[ci.MeanArrivals >= 0.03]
#medCI = ci.loc[(ci.MeanArrivals < 0.049) & (ci.MeanArrivals >= 0.03)]
worstCI = ci.loc[ci.MeanArrivals < 0.03]
bestCI = bestCI.index.tolist()
#medCI = medCI.index.tolist()
worstCI = worstCI.index.tolist()

categories = pd.DataFrame(index = range(1,5), columns = ['DT','CI'])
categories.loc[1,:] = [bestDT, bestCI]
categories.loc[2,:] = [bestDT, worstCI]
categories.loc[3,:] = [worstDT, bestCI]
categories.loc[4,:] = [worstDT, bestCI]
# categories.loc[5,:] = [medDT, medCI]
# categories.loc[6,:] = [medDT, worstCI]
# categories.loc[7,:] = [worstDT, bestCI]
# categories.loc[8,:] = [worstDT, medCI]
# categories.loc[9,:] = [worstDT, worstCI]

categories.to_csv('../Data/predict/categories.csv')
