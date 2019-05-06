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
attendance['Week'] = attendance['Date'].dt.to_period('W').apply(lambda r: r.start_time)

attendance = attendance.groupby(['WeekDay', 'Week'])['ClientID'].sum().reset_index()

lags = [1, 1, 4, 1, 6, 1, 1]
for k in range(1,8):
    Friday = attendance.loc[attendance.WeekDay == k]
    Friday['Week'] = Friday['Week'].apply(lambda x: x.date())

    Friday = Friday.loc[:,['Week','ClientID']]
    Friday.columns = ['Date','Arrivals']
    #Friday.plot()
    #pyplot.show()

    #autocorrelation_plot(Friday.Arrivals)
    #pyplot.show()

    model = ARIMA(Friday.Arrivals, order=(lags[k-1],1,0))
    model_fit = model.fit(disp=0)
    print(model_fit.summary())
    # plot residual errors
    residuals = pd.DataFrame(model_fit.resid)
    residuals.plot()
    pyplot.show()
    residuals.plot(kind='kde')
    pyplot.show()
    print(residuals.describe())
