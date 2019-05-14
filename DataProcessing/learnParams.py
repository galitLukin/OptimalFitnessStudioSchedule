import pandas as pd
import glob
import datetime
import matplotlib.pyplot as plt
import numpy as np

import cleaning

def main():

    attendance = cleaning.filterandGroup()
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

    dt = perDTCI.groupby(['WeekDay','Start time'])['avgArrivals'].mean().reset_index()
    dt = dt.loc[:,['WeekDay','Start time','avgArrivals']]
    dt.columns = ['WeekDay','StartTime','avgArrivals']
    dt.WeekDay = dt.WeekDay.apply(lambda x: days.index(x) + 1)
    dt.StartTime = dt.StartTime.apply(lambda t: int(((t.hour + t.minute/60.0) - 6)*2+1))

    row = len(dt)
    for d in range(1,8):
        for t in range(1,29):
            if len(dt.loc[(dt.WeekDay == d) & (dt.StartTime == t)]) == 0 and t > 1:
                row = row + 1
                closeArrivals = cleaning.fillTimeSlots(dt, d, t)
                dt.at[row,:] = [d,t,closeArrivals]

    dt.to_csv('../Data/output/dt.csv', index = False)

    dtci = perDTCI.groupby(['WeekDay','Start time','Description','Staff'])['avgArrivals'].mean().reset_index()
    dtci = dtci.loc[:,['WeekDay','Start time','Description','Staff','avgArrivals']]
    dtci.columns = ['WeekDay','StartTime','Description','Staff','avgArrivals']
    dtci.WeekDay = dtci.WeekDay.apply(lambda x: days.index(x) + 1)
    dtci.StartTime = dtci.StartTime.apply(lambda t: int(((t.hour + t.minute/60.0) - 6)*2+1))
    dtci.Description = dtci.Description.apply(lambda x: cleaning.classes.index(x) + 1)
    dtci.Staff = dtci.Staff.apply(lambda x: cleaning.instructors.index(x) + 1)
    dtci.to_csv('../Data/output/dtci.csv', index = False)


main()
