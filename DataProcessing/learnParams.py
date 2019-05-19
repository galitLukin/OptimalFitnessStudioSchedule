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

    dt = perDTCI.groupby(['WeekDay','Start time']).agg({'avgArrivals': [ 'mean','count']}).reset_index()
    dt.columns = ["_".join(x) for x in dt.columns.ravel()]
    dt.columns = ['WeekDay','StartTime','avgArrivals','classCount']
    dt = dt.loc[(dt.classCount >= 5)]
    dt = dt.loc[:,['WeekDay','StartTime','avgArrivals']]
    dt.WeekDay = dt.WeekDay.apply(lambda x: days.index(x) + 1)
    dt.StartTime = dt.StartTime.apply(lambda t: int(((t.hour + t.minute/60.0) - 6)*2+1))

    cPop = perDTCI.groupby(['Description'])['avgArrivals'].mean().reset_index()
    cPop = cPop.loc[:,['Description','avgArrivals']]
    cPop.Description = cPop.Description.apply(lambda x: cleaning.classes.index(x) + 1)
    cPop.to_csv('../Data/output/c.csv', index = False)

    iPop = perDTCI.groupby(['Staff'])['avgArrivals'].mean().reset_index()
    iPop = iPop.loc[:,['Staff','avgArrivals']]
    iPop.Staff = iPop.Staff.apply(lambda x: cleaning.instructors.index(x) + 1)
    iPop.to_csv('../Data/output/i.csv', index = False)

    row = len(dt)
    for d in range(1,8):
        for t in range(1,29):
            if len(dt.loc[(dt.WeekDay == d) & (dt.StartTime == t)]) == 0:
                row = row + 1
                closeArrivals = cleaning.fillTimeSlots(dt, d, t)
                dt.at[row,:] = [d,t,closeArrivals]

    dt.to_csv('../Data/output/dt.csv', index = False)

    dtci = perDTCI.groupby(['WeekDay','Start time','Description','Staff']).agg({'avgArrivals': [ 'mean','count']}).reset_index()
    dtci.columns = ["_".join(x) for x in dtci.columns.ravel()]
    dtci.columns = ['WeekDay','Start time','Description','Staff','avgArrivals','classCount']
    dtci = dtci.loc[(dtci.classCount >= 5)]
    dtci = dtci.loc[:,['WeekDay','Start time','Description','Staff','avgArrivals']]
    dtci.columns = ['WeekDay','StartTime','Description','Staff','avgArrivals']
    dtci.WeekDay = dtci.WeekDay.apply(lambda x: days.index(x) + 1)
    dtci.StartTime = dtci.StartTime.apply(lambda t: int(((t.hour + t.minute/60.0) - 6)*2+1))
    dtci.Description = dtci.Description.apply(lambda x: cleaning.classes.index(x) + 1)
    dtci.Staff = dtci.Staff.apply(lambda x: cleaning.instructors.index(x) + 1)
    row = len(dtci)
    for d in range(1,8):
        print(d)
        for t in range(1,29):
            for c in range(1,9):
                for i in range(1,19):
                    if len(dtci.loc[(dtci.WeekDay == d) & (dtci.StartTime == t) &(dtci.Staff == i) & (dtci.Description == c)]) > 0:
                        continue
                    else:
                        avgArrivals = cleaning.fillMissing(dtci, t, c, i)
                        row = row + 1
                        if avgArrivals > 0:
                            dtci.at[row,:] = [d,t,c,i,avgArrivals]
                        elif len(ci.loc[(ci.Staff == i) & (ci.Description == c)]) > 0:
                            ciArrivals = sum(ci.loc[(ci.Staff == i) & (ci.Description == c),'avgArrivals'])
                            dtArrivals = sum(dt.loc[(dt.WeekDay == d) & (dt.StartTime == t),'avgArrivals'])
                            cArrivals = sum(cPop.loc[(cPop.Description == c),'avgArrivals'])
                            iArrivals = sum(iPop.loc[(iPop.Staff == i),'avgArrivals'])
                            avgArrivals = (ciArrivals + dtArrivals + cArrivals + iArrivals)/4.0
                            dtci.at[row,:] = [d,t,c,i,avgArrivals]
                        else:
                            dtArrivals = sum(dt.loc[(dt.WeekDay == d) & (dt.StartTime == t),'avgArrivals'])
                            cArrivals = sum(cPop.loc[(cPop.Description == c),'avgArrivals'])
                            iArrivals = sum(iPop.loc[(iPop.Staff == i),'avgArrivals'])
                            avgArrivals = (cArrivals + dtArrivals + iArrivals)/3.0
                            dtci.at[row,:] = [d,t,c,i,avgArrivals]
    dtci.to_csv('../Data/output/dtci.csv', index = False)


main()
