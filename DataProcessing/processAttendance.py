import pandas as pd
import glob
import datetime

import cleaning
import uncertainty

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

uncertainty.buildFirstUset(attendance)
uncertainty.buildRanges4(attendance)
#uncertainty.createUncertaintySet(u)
