import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from random import shuffle

import cleaning

D = 7
T = 28
C = 8
I = 18

attendance = pd.read_csv('../Data/output/attendanceGrouped.csv')
attendance.columns = ['Date', 'StartTime', 'Description', 'Staff', 'ClientID']

attendance['Date'] = pd.to_datetime(attendance['Date'])
attendance = attendance.loc[attendance['Date'] > '2019-02-01']
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
plt.tight_layout()
plt.savefig('../Data/output/graphs/new/perWeekDay.png')
plt.show()

times = attendance.groupby('StartTime')["ClientID"].mean().reset_index()
times['StartTime'] = times.StartTime.apply(lambda t: t.hour + t.minute/60.0)
times = times.reset_index(drop=True)
plt.bar(times.StartTime, times.ClientID, align='center', alpha=0.5, width=0.5)
#plt.xticks(day.WeekDay, days)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Hour')
plt.tight_layout()
plt.savefig('../Data/output/graphs/new/perHour.png')
plt.show()

daytimes = attendance.groupby(['WeekDay','StartTime']).agg({"ClientID":['mean','count']}).reset_index()
daytimes['StartTime'] = daytimes.StartTime.apply(lambda t: t.hour + t.minute/60.0)
daytimes.columns = ["_".join(x) for x in daytimes.columns.ravel()]
daytimes.at[:,'dt'] = daytimes.apply(lambda x: x.WeekDay_ + '_' + str(x.StartTime_),axis=1)
daytimes = daytimes.loc[(daytimes.ClientID_count >= 5)]
daytimes = daytimes.loc[:,['dt','ClientID_mean']]
daytimes = daytimes.sort_values('ClientID_mean')
daytimes = daytimes.reset_index(drop=True)
plt.bar(daytimes.dt, daytimes.ClientID_mean, align='center', alpha=0.5)
plt.xticks(rotation=80)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Day+Time')
plt.tight_layout()
plt.savefig('../Data/output/graphs/new/perDayTime.png')
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
classes.at[:,'classesShort'] = classes.Description.apply(lambda x: cleaning.classesShort[cleaning.classes.index(x)])
plt.xticks(classes.Description, classes.classesShort)
plt.xticks(rotation=30)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Class Type')
plt.tight_layout()
plt.savefig('../Data/output/graphs/new/perClass.png')
plt.show()

instructorsPrivate = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R"]
shuffle(instructorsPrivate)
print(instructorsPrivate)
instructors = attendance.groupby('Staff')["ClientID"].mean().reset_index()
instructors.Staff = instructors.Staff.apply(lambda x: instructorsPrivate[cleaning.instructors.index(x)])
instructors = instructors.sort_values('ClientID')
instructors = instructors.reset_index(drop=True)
plt.bar(instructors.Staff, instructors.ClientID, align='center', alpha=0.5)
plt.xticks(rotation=30)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Instructor')
plt.tight_layout()
plt.savefig('../Data/output/graphs/new/perInstructor.png')
plt.show()

instructorsClass = attendance.groupby(['Staff','Description']).agg({"ClientID":['mean','count']}).reset_index()
instructorsClass.Staff = instructorsClass.Staff.apply(lambda x: instructorsPrivate[cleaning.instructors.index(x)])
instructorsClass.Description = instructorsClass.Description.apply(lambda x: cleaning.classesShort[cleaning.classes.index(x)])
instructorsClass.columns = ["_".join(x) for x in instructorsClass.columns.ravel()]
instructorsClass.at[:,'ic'] = instructorsClass.apply(lambda x: x.Description_ + '_' + x.Staff_,axis=1)
instructorsClass = instructorsClass.loc[(instructorsClass.ClientID_count >= 5)]
instructorsClass = instructorsClass.loc[:,['ic','ClientID_mean']]
instructorsClass = instructorsClass.sort_values('ClientID_mean')
instructorsClass = instructorsClass.reset_index(drop=True)
plt.bar(instructorsClass.ic, instructorsClass.ClientID_mean, align='center', alpha=0.5)
plt.xticks(rotation=80)
plt.ylabel('Average Amount of Customers')
plt.title('Average Amount of Customers Per Class+Instructor')
plt.tight_layout()
plt.savefig('../Data/output/graphs/new/perClassInstructor.png')
plt.show()

df = pd.DataFrame(index = range(18), columns = ['Instructor','Val'])
df.Instructor = cleaning.instructors
df.Val = instructorsPrivate
df.to_csv('../Data/output/graphs/new/instructorKey.csv', index = False)

instructorsClassSlot = attendance.loc[(attendance.Staff == "CATES,SHELLEY") & (attendance.Description == "INFERNOHOTPILATES")]
instructorsClass = instructorsClassSlot.groupby(['WeekDay','StartTime']).agg({"ClientID":['mean','count']}).reset_index()
instructorsClass.columns = ["_".join(x) for x in instructorsClass.columns.ravel()]
instructorsClass.StartTime_ = instructorsClass.StartTime_.apply(lambda x: x.time())
instructorsClass.sort_values('ClientID_mean').to_csv('../Data/output/graphs/new/IHP.csv', index = False)

instructorsClassSlot = attendance.loc[(attendance.Staff == "PHAN,STEVEN") & (attendance.Description == "HOT26")]
instructorsClass = instructorsClassSlot.groupby(['WeekDay','StartTime']).agg({"ClientID":['mean','count']}).reset_index()
instructorsClass.columns = ["_".join(x) for x in instructorsClass.columns.ravel()]
instructorsClass.StartTime_ = instructorsClass.StartTime_.apply(lambda x: x.time())
instructorsClass.sort_values('ClientID_mean').to_csv('../Data/output/graphs/new/HOT26.csv', index = False)

diverseSlots = attendance.loc[:, ['WeekDay','StartTime','Staff','Description']].drop_duplicates()
diverseSlots = diverseSlots.groupby(['WeekDay','StartTime']).count().reset_index()
diverseSlots = diverseSlots.loc[(diverseSlots.Staff >=5)]
diverseSlots = diverseSlots.loc[:,['WeekDay','StartTime']]
diverseSlots = pd.merge(diverseSlots, attendance,on = ['WeekDay','StartTime'],how ='inner')
instructorsClass = diverseSlots.groupby(['WeekDay','StartTime','Staff','Description']).agg({"ClientID":['mean','count']}).reset_index()
instructorsClass.columns = ["_".join(x) for x in instructorsClass.columns.ravel()]
instructorsClass.StartTime_ = instructorsClass.StartTime_.apply(lambda x: x.time())
instructorsClass.Staff_ = instructorsClass.Staff_.apply(lambda x: instructorsPrivate[cleaning.instructors.index(x)])
instructorsClass.sort_values(['WeekDay_','StartTime_','ClientID_mean']).to_csv('../Data/output/graphs/new/diverseSlots.csv', index = False)
