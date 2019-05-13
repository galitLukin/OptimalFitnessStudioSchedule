import pandas as pd
import datetime

import cleaning
import mapping
import rankings

D = 7
T = 28
C = 8
I = 18

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

    DTCI.columns = ["_".join(x) for x in DTCI.columns.ravel()]
    DT.columns = ["_".join(x) for x in DT.columns.ravel()]
    CI.columns = ["_".join(x) for x in CI.columns.ravel()]
    Daily.columns = ["_".join(x) for x in Daily.columns.ravel()]

    DT.to_csv('../Data/processed/dt.csv')

    DT = mapping.mapMissingDT(DT)
    CI = mapping.mapMissingCI(CI)

    cols = ['MinVal','MaxVal']
    # uDaily = pd.DataFrame(columns=cols)
    # uDaily.at['Weekly',:] = [min(WEEK.Arrivals), max(WEEK.Arrivals)]
    # for d in range(1,D+1):
    #     cell = Daily.loc[(Daily.WeekDay_ == d), :]
    #     cell = cell.reset_index(drop=True)
    #     uDaily.at['D_{}'.format(d),'MinVal'] = int(cell.Arrivals_q2[0])
    #     uDaily.at['D_{}'.format(d),'MaxVal'] = int(cell.Arrivals_q4[0])
    # uDaily.to_csv('../Data/output/staticUDaily.csv', index = False)
    category1 = pd.read_csv('../Data/processed/category1.csv')
    category2 = pd.read_csv('../Data/processed/category2.csv')
    cols = []
    for k in range(1,19):
        cols.append('I_{}'.format(k))
    u = pd.DataFrame(columns=cols)
    for d in range(1,D+1):
        print(d)
        for t in range(1,T+1):
            print(t)
            for c in range(1,C+1):
                for i in range(1,I+1):
                    s = rankings.getPoints(d,t,c,i)
                    cell = DTCI.loc[(DTCI.WeekDay_ == d) & (DTCI.StartTime_ == t) & (DTCI.Description_ == c) & (DTCI.Staff_ == i), :]
                    if cell.empty:
                        dtcell = DT.loc[(DT.WeekDay_ == d) & (DT.StartTime_ == t), :]
                        cicell = CI.loc[(CI.Description_ == c) & (CI.Staff_ == i), :]
                        dtcell = dtcell.reset_index(drop=True)
                        cicell = cicell.reset_index(drop=True)
                        if cicell.Arrivals_q2[0] == 0:
                            # teacher does not teach class
                            u.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = 0
                        else:
                            u.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(max(dtcell.Arrivals_q2[0], cicell.Arrivals_q2[0])) + s
                    else:
                        if len(category1.loc[(category1.WeekDay == d) & (category1.StartTime == t) & (category1.Description == c) & (category1.Staff == i), :]) > 0:
                            u.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = 23 + s
                        elif len(category2.loc[(category2.WeekDay == d) & (category2.StartTime == t) & (category2.Description == c) & (category2.Staff == i), :]) > 0:
                            u.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = 10 + s
                        else:
                            cell = cell.reset_index(drop=True)
                            u.at['DTC_{}_{}_{}'.format(d,t,c),'I_{}'.format(i)] = int(cell.Arrivals_q2[0]) + s

    u.to_csv('../Data/output/U.csv', index = False)
