import pandas as pd
import numpy as np
from pandas.plotting import autocorrelation_plot
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
import statsmodels.api as sm
import itertools
import warnings
from datetime import date, timedelta
warnings.filterwarnings("ignore")

import cleaning

D = 7
T = 28
C = 8
I = 18

attendance = cleaning.filterandGroup()
y_truth_attendance = [29,55,21,54,56,85,86]
y_truth_classes = [2,3,2,4,5,6,6]
y_truth = [float(x)/y for x,y in zip(y_truth_attendance,y_truth_classes)]
test_week = pd.to_datetime(['2019-06-01', '2019-06-02', '2019-06-03', '2019-06-04', '2019-06-05', '2019-06-06','2019-06-07'])

attendance.columns = ['Date', 'StartTime', 'Description', 'Staff', 'ClientID']
daily = attendance.groupby('Date').agg({'ClientID':'sum','StartTime': 'count'})
daily.at[:,'AttendancePerClassCount'] = daily.apply(lambda x: float(x.ClientID)/x.StartTime,axis=1)
for k in range(len(y_truth)):
    daily.at[test_week[k],'AttendancePerClassCount'] = y_truth[k]
print(len(daily.index))

daily = daily.loc[:,'AttendancePerClassCount']
lately = daily.index >= '2019-02-01'
daily = daily.loc[lately]
daily.index = pd.to_datetime(daily.index)


#no missing!
# d = daily.index
# date_set = set(d[0] + timedelta(x) for x in range((d[119] - d[0]).days))
# missing = sorted(date_set - set(d))
# print(missing)

# daily.plot()
# plt.show()
# p = d = q = range(0, 2)
# pdq = list(itertools.product(p, d, q))
# seasonal_pdq = [(x[0], x[1], x[2], 7) for x in list(itertools.product(p, d, q))]

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
# ARIMA(0, 0, 1)x(0, 1, 1, 7)7 - AIC:517.046092883731

daily = daily.reset_index()
mod = sm.tsa.statespace.SARIMAX(daily.AttendancePerClassCount,
                                order=(0, 0, 1),
                                seasonal_order=(0, 1, 1, 7),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
results = mod.fit(disp = 0)
print(results.summary().tables[1])
pred = results.get_prediction(start=121, end=127,dynamic=False)
results.plot_diagnostics(figsize=(16, 8))
plt.show()
pred_ci = pred.conf_int()
ax = daily.AttendancePerClassCount.plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))
ax.fill_between(pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color='k', alpha=.2)
ax.set_xlabel('Date')
plt.xticks([1,30,60,90], ['2019-02','2019-03','2019-04','2019-05'])
ax.set_ylabel('Arrivals')
plt.title('Demand Over Time')
plt.legend()
plt.show()

y_forecasted = pred.predicted_mean
mse = ((y_forecasted - y_truth) ** 2).mean()
print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))
print('The Root Mean Squared Error of our forecasts is {}'.format(round(np.sqrt(mse), 2)))

data = pd.DataFrame(columns = ['MinVal','MaxVal'])
i = 0
s = [0,0]
for index, row in pred_ci.iterrows():
    l = row['lower AttendancePerClassCount'] * 6
    u = row['upper AttendancePerClassCount'] * 6
    data.at[i,:] = [l,u]
    i = i + 1
    s[0] = s[0] + l
    s[1] = s[1] + u
data.at[i,:] = [s[0], s[1]]
data.to_csv('../Data/output/SARIMAdailyU.csv', index = False)
