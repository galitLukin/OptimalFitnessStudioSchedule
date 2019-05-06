import pandas as pd
import numpy as np
from pandas.plotting import autocorrelation_plot
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA


import cleaning

D = 7
T = 28
C = 8
I = 18

def findCategory(dt,ci,categories):
    for index, row in categories.iterrows():
        if dt in row.DT and ci in row.CI:
            return index
    return

attendance = pd.read_csv('../Data/predict/attendanceGrouped.csv')
categories = pd.read_csv('../Data/predict/categories.csv')

#filter old instructors
attendance.Staff = attendance.Staff.apply(lambda instructor: cleaning.filterInstructors(instructor))
attendance = attendance.loc[attendance.Staff != "Filter"]

attendance.columns = ['Date', 'StartTime', 'Description', 'Staff', 'ClientID']
attendance['Date'] = pd.to_datetime(attendance['Date'])
attendance['StartTime'] = pd.to_datetime(attendance['StartTime'])
attendance['WeekDay'] = attendance.Date.apply(lambda x: x.strftime("%A"))

attendance.Staff = attendance.Staff.apply(lambda x : cleaning.instructors.index(x) + 1)
attendance.Description = attendance.Description.apply(lambda x : cleaning.classes.index(x) + 1)
attendance.WeekDay = attendance.WeekDay.apply(lambda x : cleaning.weekDays.index(x) + 1)
attendance.StartTime = attendance.StartTime.apply(lambda x : int(((x.hour + x.minute/60.0) - 6)*2+1))

gr = attendance.groupby(pd.Grouper(key='Date',freq='W-MON'))
weeklyArrivals = pd.DataFrame(columns= ['Arrivals'])

for name,group in gr:
    weeklyArrivals.loc[name.date(),'Arrivals'] = sum(group.ClientID)
#print(weeklyArrivals)
#weeklyArrivals.plot()
#pyplot.show()

#autocorrelation_plot(weeklyArrivals)
#pyplot.show()

model = ARIMA(weeklyArrivals, order=(4,1,0))
model_fit = model.fit(disp=0)
print(model_fit.summary())
# plot residual errors
residuals = pd.DataFrame(model_fit.resid)
residuals.plot()
pyplot.show()
residuals.plot(kind='kde')
pyplot.show()
print(residuals.describe())
