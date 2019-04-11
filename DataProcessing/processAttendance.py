import pandas as pd
import glob

attendanceList = []
files = glob.glob('../Data/raw/' + "/*.xlsx")

for f in files:
    temp = pd.read_excel(f)
    temp = temp.loc[:,['Date', 'Start time', 'End time', 'Description', 'Staff', 'Client ID', 'Status']]
    attendanceList.append(temp)

attendance = pd.concat(attendanceList)
print(len(attendance))
#take only users that arrived
attendance = attendance.loc[(attendance['Status'] == 'Signed in') | (attendance['Status'] == 'Reserved')]
print(len(attendance))
#take only classes being offered now
temp = attendance.loc[:,['Description','Date','Start time']].drop_duplicates()
print(temp.groupby('Description').count())
# attendance = attendance.loc[(attendance['Description'] == 'HOT HATHA SCULPT') | (attendance['Description'] == ''INFERNO HOT PILATES'')\
#                             | (attendance['Description'] == 'CLASSIC 90') | (attendance['Description'] == 'Reserved')\
#                             | ]
#take only instructors working now
temp = attendance.loc[:,['Description','Date','Start time','Staff']].drop_duplicates()
print(temp.groupby('Staff').count())
attendance = attendance.loc[:,['Date', 'Start time', 'End time', 'Description', 'Staff', 'Client ID']]
attendance.to_csv('../Data/processed/attendance.csv', index = False)
