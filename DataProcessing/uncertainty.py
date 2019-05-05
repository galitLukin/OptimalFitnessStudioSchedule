import pandas as pd
import datetime

import cleaning

D = 7
T = 28
C = 8
I = 18

def createUncertaintySet(constraintTypes):
    title = constraintTypes.index.tolist()
    mi = constraintTypes.MinVal.tolist()
    ma = constraintTypes.MaxVal.tolist()
    u = pd.DataFrame(index = range(84672), columns=['D','T','C','I','MinVal','MaxVal'])
    k = 0
    for d in range(1,D+1):
        print(d)
        for t in range(1,T+1):
            for c in range(1,C+1):
                for i in range(1,I+1):
                    ind = title.index('Time{}'.format(t))
                    u.loc[k] = pd.Series({'D':d, 'T':t, 'C':c, 'I':i, 'MinVal':mi[ind], 'MaxVal':ma[ind]})
                    k+=1
                    ind = title.index('Class{}.0'.format(c),)
                    u.loc[k] = pd.Series({'D':d, 'T':t, 'C':c, 'I':i, 'MinVal':mi[ind] , 'MaxVal':ma[ind]})
                    k+=1
                    ind = title.index('Instructor{}.0'.format(i))
                    u.loc[k] = pd.Series({'D':d, 'T':t, 'C':c, 'I':i, 'MinVal':mi[ind] , 'MaxVal':ma[ind]})
                    k+=1
    u.to_csv('../Data/output/staticU.csv', index = False)

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
    #DTCI = attendance.groupby(['StartTime','Description','Staff','WeekDay'], as_index=False).agg({"Arrivals": ["max", "min"]})
    #range per day,time
    #DT = attendance.groupby(['StartTime','WeekDay'], as_index=False).agg({"Arrivals": ["max", "min"]})
    #range per day
    D = attendance.groupby(['WeekDay'], as_index=False).agg(f)
    #range per time
    T = attendance.groupby(['StartTime'], as_index=False).agg(f)
    #range per class type, instructor
    #CI = attendance.groupby(['Description','Staff'], as_index=False).agg({"Arrivals": ["max", "min"]})
    #range per class type, instructor
    C = attendance.groupby(['Description'], as_index=False).agg(f)
    #range per class type, instructor
    I = attendance.groupby(['Staff'], as_index=False).agg(f)

    #DTCI.columns = ["_".join(x) for x in DTCI.columns.ravel()]
    #DT.columns = ["_".join(x) for x in DT.columns.ravel()]
    #CI.columns = ["_".join(x) for x in CI.columns.ravel()]
    D.columns = ["_".join(x) for x in D.columns.ravel()]
    T.columns = ["_".join(x) for x in T.columns.ravel()]
    C.columns = ["_".join(x) for x in C.columns.ravel()]
    I.columns = ["_".join(x) for x in I.columns.ravel()]

    #DTCI.to_csv('../Data/processed/DTCIdemand.csv', index = False)
    #DT.to_csv('../Data/processed/DTdemand.csv', index = False)
    #CI.to_csv('../Data/processed/CIdemand.csv', index = False)
    #D.to_csv('../Data/processed/Ddemand.csv', index = False)
    T.to_csv('../Data/processed/Tdemand.csv', index = False)
    C.to_csv('../Data/processed/Cdemand.csv', index = False)
    I.to_csv('../Data/processed/Idemand.csv', index = False)
    #WEEK = pd.read_csv('../Data/processed/WEEKdemand.csv')

    #constraints = ['Weekly','Day1','Day2','Day3','Day4','Day5','Day6','Day7']
    cols = ['MinVal', 'MaxVal']
    u = pd.DataFrame(columns=cols)
    # print("Weekly demand range: ", min(WEEK.Arrivals), max(WEEK.Arrivals))
    # u.at['Weekly',:] = [min(WEEK.Arrivals), max(WEEK.Arrivals)]
    # for index, row in D.iterrows():
    #     #print("Daily demand range: ", "Day ", row.WeekDay_, row.Arrivals_min, row.Arrivals_max)
    #     u.at['Day{}'.format(i),:] = [row.Arrivals_min, row.Arrivals_max]
    #     i=i+1
    # for index, row in CI.iterrows():
    #     #print("Class/Instructor demand range: ", "Class ", row.Description_, "Instructor ", row.Staff_, row.Arrivals_min, row.Arrivals_max)
    #     u.at['Class{}Staff{}'.format(row.Description_,row.Staff_),:] = [row.Arrivals_min, row.Arrivals_max]
    for index, row in C.iterrows():
        #print("Class demand range: ", "Slot ", row.Description_, row.Arrivals_min, row.Arrivals_max)
        u.at['Class{}'.format(row.Description_),:] = [row.Arrivals_q2, row.Arrivals_q4]
    for index, row in I.iterrows():
        #print("Instructor demand range: ", "Instructor ", row.Staff_, row.Arrivals_min, row.Arrivals_max)
        u.at['Instructor{}'.format(row.Staff_),:] = [row.Arrivals_q2, row.Arrivals_q4]
    u = cleaning.fillTimeSlots(u,T)

    u.to_csv('../Data/processed/staticPreU.csv', index = False)
    return u


def buildRanges3(attendance):
    f = {'Arrivals': [q2,q4]}
    #range per class
    DTCI = attendance.groupby(['StartTime','Description','Staff','WeekDay'], as_index=False).agg(f)

    DTCI.columns = ["_".join(x) for x in DTCI.columns.ravel()]

    DTCI.to_csv('../Data/processed/DTCIdemand.csv', index = False)

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
                        uMin.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = 0
                        uMax.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = 0
                    else:
                        cell = cell.reset_index(drop=True)
                        uMin.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(cell.Arrivals_q2[0])
                        uMax.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(cell.Arrivals_q4[0])

    uMin.to_csv('../Data/output/staticUMin.csv', index = False)
    uMax.to_csv('../Data/output/staticUMax.csv', index = False)

def buildRanges4(attendance):
    f = {'Arrivals': [q2,q4]}
    #range per class
    DTCI = attendance.groupby(['StartTime','Description','Staff','WeekDay'], as_index=False).agg(f)
    #range per day and time
    DT = attendance.groupby(['StartTime','WeekDay'], as_index=False).agg(f)
    #range per class type, instructor
    CI = attendance.groupby(['Description','Staff'], as_index=False).agg(f)

    DTCI.columns = ["_".join(x) for x in DTCI.columns.ravel()]
    DT.columns = ["_".join(x) for x in DT.columns.ravel()]
    CI.columns = ["_".join(x) for x in CI.columns.ravel()]

    #DTCI.to_csv('../Data/processed/DTCIdemand.csv', index = False)

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
