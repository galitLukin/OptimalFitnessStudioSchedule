import pandas as pd

import cleaning

D = 7
T = 28
C = 8
I = 18

def similarDays(dt, t, isweekend):
    if isweekend:
        return dt.loc[(dt.StartTime_ == t) & (dt.WeekDay_ >= 6)]
    else:
        return dt.loc[(dt.StartTime_ == t) & (dt.WeekDay_ <= 5)]

def match(dt, fulldt, t, isweekend, i):
    tMatch = similarDays(dt, t, isweekend)
    if len(tMatch) > 0:
        fulldt.loc[i,'Arrivals_q2'] = tMatch.Arrivals_q2.mean()
        fulldt.loc[i,'Arrivals_q4'] = tMatch.Arrivals_q4.mean()
    else:
        valsSmall, valsBig = [], []
        prev, next = 1, 1
        while t - prev >= 1 and len(tMatch) == 0:
            tMatch = similarDays(dt, t - prev, isweekend)
            prev = prev + 1
        if t - prev >= 1:
            valsSmall.append(tMatch.Arrivals_q2.mean())
            valsBig.append(tMatch.Arrivals_q4.mean())
        while t + next <= 28 and len(tMatch) == 0:
            tMatch = similarDays(dt, t + next, isweekend)
            next = next + 1
        if t + next <= 28:
            valsSmall.append(tMatch.Arrivals_q2.mean())
            valsBig.append(tMatch.Arrivals_q4.mean())
        if len(valsSmall) > 1:
            fulldt.loc[i,'Arrivals_q4']  = ( prev * valsBig[1] + next * valsBig[0] ) / ( prev + next )
            fulldt.loc[i,'Arrivals_q2'] = ( prev * valsSmall[1] + next * valsSmall[0] ) / ( prev + next )
        else:
            fulldt.loc[i,'Arrivals_q4']  = valsBig[0]
            fulldt.loc[i,'Arrivals_q2'] = valsSmall[0]
    return fulldt

def mapMissingDT(dt):
    fulldt = pd.DataFrame(index = range(196), columns = dt.columns)
    i = 0
    for d in range(1,D+1):
        for t in range(1,T+1):
            dtPair = dt.loc[(dt.WeekDay_ == d) & (dt.StartTime_ == t)]
            if len(dtPair) > 0:
                dtPair = dtPair.reset_index(drop=True)
                fulldt.loc[i,:] = dtPair.loc[0,:]
                i = i + 1
                continue
            fulldt.loc[i,'StartTime_'] = t
            fulldt.loc[i,'WeekDay_'] = d
            if d <= 5:
                fulldt = match(dt, fulldt, t, False, i)
            else:
                fulldt = match(dt, fulldt, t, True, i)
            i = i + 1
    fulldt = fulldt.loc[:,['StartTime_', 'WeekDay_', 'Arrivals_q2', 'Arrivals_q4']]
    fulldt.to_csv('../Data/processed/fulldt.csv', index = False)
    return fulldt

def mapMissingCI(ci):
    instructorClass = pd.read_csv('../Data/input/IntstructorClass.csv')
    instructorClass.columns = ['Instructors'] + cleaning.classes
    fullci = pd.DataFrame(index = range(144), columns = ci.columns)
    k = 0
    for c in range(1,C+1):
        for i in range(1,I+1):
            if instructorClass.at[i-1,cleaning.classes[c-1]] == 1:
                ciPair = ci.loc[(ci.Description_ == c) & (ci.Staff_ == i)]
                if len(ciPair) > 0:
                    ciPair = ciPair.reset_index(drop=True)
                    fullci.loc[k,:] = ciPair.loc[0,:]
                else:
                    fullci.loc[k,'Description_'] = c
                    fullci.loc[k,'Staff_'] = i
                    onlyI = ci.loc[ci.Staff_ >= i]
                    fullci.loc[k,'Arrivals_q4'] = onlyI.Arrivals_q4.mean()
                    fullci.loc[k,'Arrivals_q2'] = onlyI.Arrivals_q2.mean()
            else:
                fullci.loc[k,'Description_'] = c
                fullci.loc[k,'Staff_'] = i
                fullci.loc[k,'Arrivals_q4']  = 0
                fullci.loc[k,'Arrivals_q2'] = 0
            k = k + 1
    fullci = fullci.loc[:,['Description_', 'Staff_', 'Arrivals_q2', 'Arrivals_q4']]
    fullci.to_csv('../Data/processed/fullci.csv', index = False)
    return fullci
