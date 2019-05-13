import pandas as pd
import glob
import datetime
import matplotlib.pyplot as plt
import numpy as np

import cleaning

def main():

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

    #filter old instructors
    attendance.Staff = attendance.Staff.apply(lambda instructor: cleaning.filterInstructors(instructor))
    attendance = attendance.loc[attendance.Staff != "Filter"]

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

    attendance['Date'] = pd.to_datetime(attendance['Date'])
    attendance['WeekDay'] = attendance.Date.apply(lambda x: x.strftime("%A"))
    dailyArrivals = attendance.groupby(['Date'])['Client ID'].sum().reset_index()
    dailyArrivals.columns = ['Date','DailyArrivals']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    dtciArrivals = attendance.groupby(['Date','Start time','Description','Staff','WeekDay'])['Client ID'].sum().reset_index()
    perDTCI = pd.merge(dailyArrivals, dtciArrivals, on = 'Date', how = 'inner')
    perDTCI['avgArrivals'] = perDTCI.apply(lambda x: x['Client ID']/x.DailyArrivals,axis = 1)
    ci = perDTCI.groupby(['Description','Staff'])['avgArrivals'].mean().reset_index()
    ci = ci.loc[:,['Description','Staff','avgArrivals']]
    ci.Description = ci.Description.apply(lambda x: cleaning.classes.index(x) + 1)
    ci.Staff = ci.Staff.apply(lambda x: cleaning.instructors.index(x) + 1)
    ci.to_csv('../Data/output/ci.csv', index = False)


main()
