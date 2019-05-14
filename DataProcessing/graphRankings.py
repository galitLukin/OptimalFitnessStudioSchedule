import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cleaning

#10 cat 2
#23 cat 1

D = 7
T = 28
C = 8
I = 18

attendance = pd.read_csv('../Data/predict/attendanceGrouped.csv')
#filter old instructors
attendance.Staff = attendance.Staff.apply(lambda instructor: cleaning.filterInstructors(instructor))
attendance = attendance.loc[attendance.Staff != "Filter"]

attendance.columns = ['Date', 'StartTime', 'Description', 'Staff', 'ClientID']

attendance['Date'] = pd.to_datetime(attendance['Date'])
attendance['StartTime'] = pd.to_datetime(attendance['StartTime'])

attendance['WeekDay'] = attendance.Date.apply(lambda x: x.strftime("%A"))
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

day = attendance.groupby(['Date','WeekDay'])["ClientID"].sum().reset_index()
day = day.groupby('WeekDay')["ClientID"].mean().reset_index()
day = day.reset_index(drop=True)
plt.bar(day.WeekDay, day.ClientID, align='center', alpha=0.5)
plt.xticks(day.WeekDay, days)
plt.xticks(rotation=30)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Week Day')
plt.show()

times = attendance.groupby('StartTime')["ClientID"].mean().reset_index()
times['StartTime'] = times.StartTime.apply(lambda t: t.hour + t.minute/60.0)
times = times.reset_index(drop=True)
plt.bar(times.StartTime, times.ClientID, align='center', alpha=0.5, width=0.5)
#plt.xticks(day.WeekDay, days)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Hour')
plt.show()

classes = attendance.groupby('Description')["ClientID"].mean().reset_index()
classes = classes.sort_values('ClientID')
classes = classes.reset_index(drop=True)
b = plt.bar(classes.Description, classes.ClientID, align='center', alpha=0.5)
b[1].set_color('palevioletred')
b[5].set_color('palegreen')
b[0].set_color('gold')
b[6].set_color('lemonchiffon')
b[7].set_color('lightskyblue')
b[4].set_color('plum')
b[2].set_color('lightsalmon')
b[3].set_color('navajowhite')
classesShort =  ["SILENT HOT 26", "HOT 26", "HHF", "HHS", "IHP II",  "HOT 26 FLOW", "HOT 26+", "IHP"]
plt.xticks(classes.Description, classesShort)
plt.xticks(rotation=30)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Class Type')
plt.show()

instructorsPrivate = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R"]
instructors = attendance.groupby('Staff')["ClientID"].mean().reset_index()
instructors.Staff = instructors.Staff.apply(lambda x: instructorsPrivate[cleaning.instructors.index(x)])
instructors = instructors.sort_values('ClientID')
instructors = instructors.reset_index(drop=True)
plt.bar(instructors.Staff, instructors.ClientID, align='center', alpha=0.5)
plt.xticks(rotation=30)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Instructor')
plt.show()
