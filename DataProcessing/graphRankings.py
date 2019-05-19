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

demandmin = [685.0,685.0,685.0,676.0,669.0,626.0,685.0,685.0,681.0,676.0,653.0,635.0,685.0,685.0,681.0,676.0,661.0,635.0,682.0,682.0,685.0,673.0,658.0,632.0,682.0,682.0,678.0,673.0,650.0,632.0,682.0,682.0,678.0,673.0,658.0,632.0,677.0,671.0,667.0,662.0,655.0,621.0]
demandmax = [1326.0,1321.0,1322.0,1303.0,1289.0,1196.0,1325.0,1324.0,1314.0,1305.0,1256.0,1214.0,1322.0,1324.0,1309.0,1303.0,1270.0,1215.0,1313.0,1320.0,1324.0,1302.0,1267.0,1211.0,1321.0,1321.0,1310.0,1302.0,1251.0,1212.0,1319.0,1316.0,1308.0,1301.0,1266.0,1212.0,1307.0,1303.0,1292.0,1281.0,1267.0,1194.0]
instructorCount = [15.0,15.0,15.0,15.0,15.0,14.0,15.0,15.0,15.0,15.0,15.0,15.0,15.0,15.0,15.0,15.0,15.0,15.0,16.0,16.0,15.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,16.0,17.0,18.0,18.0,18.0,18.0,18.0]
classes = [47,47,47,45,44,39,47,47,46,45,42,40,48,47,46,45,43,40,48,47,47,45,43,40,47,47,46,45,42,40,47,47,46,45,43,40,48,47,46,45,44,40]
alphas = [0,1,2,3,4,5,6]
betas = [0,2,4,6,8,10]

res = pd.DataFrame(0.0,index = range(len(demandmin)), columns = ["Alpha", "Beta", "MinDemand", "MaxDemand", "AvgDemand", "InstructorCount", "ClassCount", "MinArrivalPerClass","MaxArrivalPerClass","AvgArrivalPerClass"])
blen = len(betas)
i = 0
for index,row in res.iterrows():
    a = int(index/blen)
    res.at[index,"Alpha"] = alphas[a]
    b = int(index%blen)
    res.at[index,"Beta"] = betas[b]
    res.at[index,"MinDemand"] = demandmin[i]
    res.at[index,"MaxDemand"] = demandmax[i]
    res.at[index,"InstructorCount"] = instructorCount[i]
    res.at[index,"ClassCount"] = classes[i]
    res.at[index,"AvgDemand"] = (demandmin[i] + demandmax[i])/2.0
    res.at[index,"MinArrivalPerClass"] = round(demandmin[i]/classes[i], 2)
    res.at[index,"MaxArrivalPerClass"] = round(demandmax[i]/classes[i], 2)
    res.at[index,"AvgArrivalPerClass"] = round(((demandmin[i] + demandmax[i])/2.0)/classes[i],2)
    i = i + 1
res.to_csv('../Data/output/results.csv', index = False)

instructors = res.loc[res.Beta == 10]
x = instructors.InstructorCount
y = (instructors.MinDemand + instructors.MaxDemand)/2.0
plt.title('Average Weekly Demand per Amount of Instructors')
plt.xlabel("Amount of Instructors")
plt.ylabel('Weekly Demand')
plt.scatter(x, y, c = "blue")
plt.savefig('instructors.png')
plt.show()

x = instructors.Alpha
y = instructors.InstructorCount
plt.title('Amount of Instructors per Alpha')
plt.xlabel("Alpha")
plt.ylabel('Amount of Instructors')
plt.plot(x, y)
plt.savefig('instructorsAlpha.png')
plt.show()

classes = res.loc[res.Alpha == 4]
x = classes.ClassCount
y = (classes.MinDemand + classes.MaxDemand)/2.0
plt.title('Average Weekly Demand per Amount of Classes')
plt.xlabel("Amount of Classes")
plt.ylabel('Weekly Demand')
plt.scatter(x, y, c = "blue")
plt.savefig('classes.png')
plt.show()

x = classes.Beta
y = classes.ClassCount
plt.title('Amount of Classes per Beta')
plt.xlabel("Beta")
plt.ylabel('Amount of Classes')
plt.plot(x, y)
plt.savefig('classesBeta.png')
plt.show()
