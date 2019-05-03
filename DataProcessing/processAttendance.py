import pandas as pd
import glob
import datetime

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
perDate = cleaning.removeOutlierWeeks(perDate)
perDate.to_csv('../Data/processed/perDate.csv', index = False)

#take only relevant dates
allDates = perDate.loc[:,'Date'].to_frame()
attendance = pd.merge(attendance, allDates, on = 'Date', how = 'inner')


#map classes and filter those that don't match
attendance.Description = attendance.Description.apply(lambda c: cleaning.currectClasses(c))
attendance = attendance.loc[attendance.Description != "Filter"]
attendance.to_csv('../Data/processed/attendance.csv', index = False)

# group clients per class
attendance = attendance.groupby(['Date','Start time','Description','Staff']).count().reset_index()
attendance['WeekDay'] = attendance.Date.apply(lambda x: x.strftime("%A"))
attendance.to_csv('../Data/processed/attendanceGrouped.csv', index = False)


#########outputs for Julia################
attendance.columns = ['Date', 'StartTime', 'Description', 'Staff', 'Arrivals', 'WeekDay']
#filter old instructors
attendance.Staff = attendance.Staff.apply(lambda instructor: cleaning.filterInstructors(instructor))
attendance = attendance.loc[attendance.Staff != "Filter"]

#get the last week's schedule
lastWeek = '2019-04-22 00:00:00'
lastWeek = datetime.datetime.strptime(lastWeek, '%Y-%m-%d %H:%M:%S')
lastWeekAttendance = attendance.loc[attendance['Date'] >= lastWeek]

########make feasible
lastWeekAttendance.at[914,'Description'] = "HOT26"
lastWeekAttendance.at[914,'Staff'] = "SERRANO,JIMMY"
lastWeekAttendance.at[919,'Staff'] = "LAMBERT,LUCAS"
lastWeekAttendance.at[922,'Description'] = "HOT26"
lastWeekAttendance.at[933,'Description'] = "HOT26"
lastWeekAttendance.at[940,'Description'] = "INFERNOHOTPILATES"
lastWeekAttendance.at[940,'Staff'] = "MCGRATH,SHARON"
lastWeekAttendance.at[944,'Description'] = "INFERNOHOTPILATES"
lastWeekAttendance.at[944,'Staff'] = "CATES,SHELLEY"
lastWeekAttendance.at[946,'Description'] = "HOT26"
lastWeekAttendance.at[946,'Staff'] = "MONROE,KYLAH"
##########

lastWeekAttendance.to_csv('../Data/processed/attendanceLastWeek.csv')

attendance.Staff = attendance.Staff.apply(lambda x : cleaning.instructors.index(x) + 1)
attendance.Description = attendance.Description.apply(lambda x : cleaning.classes.index(x) + 1)
attendance.WeekDay = attendance.WeekDay.apply(lambda x : cleaning.weekDays.index(x) + 1)
timeSlots = cleaning.timeSlots()
attendance.StartTime = attendance.StartTime.apply(lambda x : timeSlots.index((x.hour, x.minute)) + 1)

lastWeek = '2019-04-22 00:00:00'
lastWeek = datetime.datetime.strptime(lastWeek, '%Y-%m-%d %H:%M:%S')
lastWeekAttendance = attendance.loc[attendance['Date'] >= lastWeek]

########make feasible
lastWeekAttendance.at[914,'Description'] = 1
lastWeekAttendance.at[914,'Staff'] = 15
lastWeekAttendance.at[919,'Staff'] = 8
lastWeekAttendance.at[922,'Description'] = 1
lastWeekAttendance.at[933,'Description'] = 1
lastWeekAttendance.at[940,'Description'] = 5
lastWeekAttendance.at[940,'Staff'] = 11
lastWeekAttendance.at[944,'Description'] = 5
lastWeekAttendance.at[944,'Staff'] = 4
lastWeekAttendance.at[946,'Description'] = 1
lastWeekAttendance.at[946,'Staff'] = 12
#######

lastWeekAttendance.to_csv('../Data/output/attendanceLastWeekIndex.csv')


#range per class
DTCI = attendance.groupby(['StartTime','Description','Staff','WeekDay'], as_index=False).agg({"Arrivals": ["max", "min"]})
#range per day,time
DT = attendance.groupby(['StartTime','WeekDay'], as_index=False).agg({"Arrivals": ["max", "min"]})
#range per day
D = attendance.groupby(['WeekDay'], as_index=False).agg({"Arrivals": ["max", "min"]})
#range per time
T = attendance.groupby(['StartTime'], as_index=False).agg({"Arrivals": ["max", "min"]})
#range per class type, instructor
CI = attendance.groupby(['Description','Staff'], as_index=False).agg({"Arrivals": ["max", "min"]})
#range per class type, instructor
C = attendance.groupby(['Description'], as_index=False).agg({"Arrivals": ["max", "min"]})

DTCI.columns = ["_".join(x) for x in DTCI.columns.ravel()]
DT.columns = ["_".join(x) for x in DT.columns.ravel()]
CI.columns = ["_".join(x) for x in CI.columns.ravel()]
D.columns = ["_".join(x) for x in D.columns.ravel()]
T.columns = ["_".join(x) for x in T.columns.ravel()]
C.columns = ["_".join(x) for x in C.columns.ravel()]

DTCI.to_csv('../Data/processed/DTCIdemand.csv', index = False)
DT.to_csv('../Data/processed/DTdemand.csv', index = False)
CI.to_csv('../Data/processed/CIdemand.csv', index = False)
D.to_csv('../Data/processed/Ddemand.csv', index = False)
T.to_csv('../Data/processed/Tdemand.csv', index = False)
C.to_csv('../Data/processed/Cdemand.csv', index = False)
WEEK = pd.read_csv('../Data/processed/WEEKdemand.csv')

#constraints = ['Weekly','Day1','Day2','Day3','Day4','Day5','Day6','Day7']
cols = ['MinVal', 'MaxVal']
u = pd.DataFrame(columns=cols)
print("Weekly demand range: ", min(WEEK.Arrivals), max(WEEK.Arrivals))
u.at['Weekly',:] = [min(WEEK.Arrivals), max(WEEK.Arrivals)]
i=1
for index, row in D.iterrows():
    print("Daily demand range: ", "Day ", row.WeekDay_, row.Arrivals_max, row.Arrivals_min)
    u.at['Day{}'.format(i),:] = [row.Arrivals_min, row.Arrivals_max]
    i=i+1
for index, row in CI.iterrows():
    print("Class/Instructor demand range: ", "Class ", row.Description_, "Instructor ", row.Staff_, row.Arrivals_max, row.Arrivals_min)
    u.at['Class{}Staff{}'.format(row.Description_,row.Staff_),:] = [row.Arrivals_min, row.Arrivals_max]
for index, row in T.iterrows():
    print("Time demand range: ", "Slot ", row.StartTime_, row.Arrivals_max, row.Arrivals_min)
    u.at['Time{}'.format(row.StartTime_),:] = [row.Arrivals_min, row.Arrivals_max]
for index, row in C.iterrows():
    print("Class demand range: ", "Slot ", row.Description_, row.Arrivals_max, row.Arrivals_min)
    u.at['Class{}'.format(row.Description_),:] = [row.Arrivals_min, row.Arrivals_max]
C.to_csv('../Data/output/staticU.csv', index = False)
