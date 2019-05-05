import pandas as pd
import datetime

import cleaning

D = 7
T = 28
C = 8
I = 18

def buildFirstUset(attendance):
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

    lastWeekAttendance.to_csv('../Data/output/attendanceLastWeekIndex.csv', index = False)

def q1(x):
    return x.quantile(0.25)

def q2(x):
    return x.quantile(0.5)

def q3(x):
    return x.quantile(0.75)

def q4(x):
    return x.quantile(1)

def buildRanges(attendance):
    f = {'Arrivals': [q2,q4]}
    #range per class
    DTCI = attendance.groupby(['StartTime','Description','Staff','WeekDay'], as_index=False).agg(f)
    #range per day and time
    DT = attendance.groupby(['StartTime','WeekDay'], as_index=False).agg(f)
    #range per class type, instructor
    CI = attendance.groupby(['Description','Staff'], as_index=False).agg(f)
    #range per day
    Daily = attendance.groupby(['WeekDay'], as_index=False).agg(f)
    #weekly Arrivals
    WEEK = pd.read_csv('../Data/processed/WEEKdemand.csv')

    DTCI.columns = ["_".join(x) for x in DTCI.columns.ravel()]
    DT.columns = ["_".join(x) for x in DT.columns.ravel()]
    CI.columns = ["_".join(x) for x in CI.columns.ravel()]
    Daily.columns = ["_".join(x) for x in Daily.columns.ravel()]

    cols = ['MinVal','MaxVal']
    uDaily = pd.DataFrame(columns=cols)
    uDaily.at['Weekly',:] = [min(WEEK.Arrivals), max(WEEK.Arrivals)]
    for d in range(1,D+1):
        cell = Daily.loc[(Daily.WeekDay_ == d), :]
        cell = cell.reset_index(drop=True)
        uDaily.at['D_{}'.format(d),'MinVal'] = int(cell.Arrivals_q2[0])
        uDaily.at['D_{}'.format(d),'MaxVal'] = int(cell.Arrivals_q4[0])
    uDaily.to_csv('../Data/output/staticUDaily.csv', index = False)
    cols = []
    for k in range(1,19):
        cols.append('I_{}'.format(k))
    uMin = pd.DataFrame(columns=cols)
    uMax = pd.DataFrame(columns=cols)
    for d in range(1,D+1):
        print(d)
        for t in range(1,T+1):
            for c in range(1,C+1):
                for i in range(1,I+1):
                    cell = DTCI.loc[(DTCI.WeekDay_ == d) & (DTCI.StartTime_ == t) & (DTCI.Description_ == c) & (DTCI.Staff_ == i), :]
                    if cell.empty:
                        dtcell = DT.loc[(DT.WeekDay_ == d) & (DT.StartTime_ == t), :]
                        cicell = CI.loc[(CI.Description_ == c) & (CI.Staff_ == i), :]
                        if cicell.empty:
                            uMin.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = 0
                            uMax.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = 0
                        elif dtcell.empty:
                            cicell = cicell.reset_index(drop=True)
                            uMin.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(cicell.Arrivals_q2[0])
                            uMax.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(cicell.Arrivals_q4[0])
                        else:
                            dtcell = dtcell.reset_index(drop=True)
                            cicell = cicell.reset_index(drop=True)
                            uMin.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(max(dtcell.Arrivals_q2[0], cicell.Arrivals_q2[0]))
                            uMax.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(min(dtcell.Arrivals_q4[0], cicell.Arrivals_q4[0]))
                    else:
                        cell = cell.reset_index(drop=True)
                        uMin.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(cell.Arrivals_q2[0])
                        uMax.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(cell.Arrivals_q4[0])

    uMin.to_csv('../Data/output/staticUMin.csv', index = False)
    uMax.to_csv('../Data/output/staticUMax.csv', index = False)
