import pandas as pd
import numpy as np
from pandas.plotting import autocorrelation_plot
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
import statsmodels.api as sm
import itertools
import warnings
warnings.filterwarnings("ignore")

import cleaning

D = 7
T = 28
C = 8
I = 18

attendance = pd.read_csv('../Data/predict/attendanceGrouped.csv')

#filter old instructors
attendance.Staff = attendance.Staff.apply(lambda instructor: cleaning.filterInstructors(instructor))
attendance = attendance.loc[attendance.Staff != "Filter"]

attendance.at[1010,'Client ID'] = 82
attendance.at[1010,'Date'] = '2019-04-29'
attendance.at[1011,'Client ID'] = 105
attendance.at[1011,'Date'] = '2019-04-30'
attendance.at[1012,'Client ID'] = 109
attendance.at[1012,'Date'] = '2019-05-01'
attendance.at[1013,'Client ID'] = 73
attendance.at[1013,'Date'] = '2019-05-02'
attendance.at[1014,'Client ID'] = 111
attendance.at[1014,'Date'] = '2019-05-03'
attendance.at[1015,'Client ID'] = 53
attendance.at[1015,'Date'] = '2019-05-04'
attendance.at[1016,'Client ID'] = 113
attendance.at[1016,'Date'] = '2019-05-05'

attendance.columns = ['Date', 'StartTime', 'Description', 'Staff', 'ClientID']
# #attendance['Date'] = pd.to_datetime(attendance['Date'])
# attendance['StartTime'] = pd.to_datetime(attendance['StartTime'])
# attendance['WeekDay'] = attendance.Date.apply(lambda x: x.strftime("%A"))


# attendance.Staff = attendance.Staff.apply(lambda x : cleaning.instructors.index(x) + 1)
# attendance.Description = attendance.Description.apply(lambda x : cleaning.classes.index(x) + 1)
# attendance.WeekDay = attendance.WeekDay.apply(lambda x : cleaning.weekDays.index(x) + 1)
# attendance.StartTime = attendance.StartTime.apply(lambda x : int(((x.hour + x.minute/60.0) - 6)*2+1))
#
daily = attendance.groupby('Date')['ClientID'].sum()
# print(daily)

print(len(daily))
#
# daily.plot()
# plt.show()
p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 7) for x in list(itertools.product(p, d, q))]

# for param in pdq:
#     for param_seasonal in seasonal_pdq:
#         try:
#             mod = sm.tsa.statespace.SARIMAX(daily,
#                                             order=param,
#                                             seasonal_order=param_seasonal,
#                                             enforce_stationarity=False,
#                                             enforce_invertibility=False)
#             results = mod.fit(disp = 0)
#             print('ARIMA{}x{}7 - AIC:{}'.format(param, param_seasonal, results.aic))
#         except:
#             print("failed")
#             continue
# ARIMA(1, 1, 1)x(0, 1, 1, 7)7 - AIC:1560.5683622797435

mod = sm.tsa.statespace.SARIMAX(daily,
                                order=(1, 1, 1),
                                seasonal_order=(0, 1, 1, 7),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
results = mod.fit(disp = 0)
print(results.summary().tables[1])
pred = results.get_prediction(start=209, end=215,dynamic=False)
results.plot_diagnostics(figsize=(16, 8))
plt.show()
pred_ci = pred.conf_int()
ax = daily.plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))
ax.fill_between(pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color='k', alpha=.2)
ax.set_xlabel('Date')
plt.xticks([1,30,60,90,120,150,180,215], ['2018-10','2018-11','2018-12','2019-01','2019-02','2019-03','2019-04','2019-05'])
ax.set_ylabel('Arrivals')
plt.title('Demand Over Time')
plt.legend()
plt.show()

y_forecasted = pred.predicted_mean
y_truth = [82,105,109,73,111,53,113]
mse = ((y_forecasted - y_truth) ** 2).mean()
print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))
print('The Root Mean Squared Error of our forecasts is {}'.format(round(np.sqrt(mse), 2)))


# #print(pred.predicted_mean)
# print(pred_ci)
# data = pd.DataFrame(columns = ['MinVal','MaxVal'])
# i = 0
# s = [0,0]
# for index, row in pred_ci.iterrows():
#     data.at[i,:] = [row['lower ClientID'], row['upper ClientID']]
#     i = i + 1
#     s[0] = s[0] + row['lower ClientID']
#     s[1] = s[1] + row['upper ClientID']
# data.at[i,:] = [s[0], s[1]]
# data.to_csv('../Data/output/SARIMAdailyU.csv', index = False)
