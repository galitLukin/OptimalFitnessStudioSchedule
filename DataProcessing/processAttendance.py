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
attendance = attendance.loc[(attendance['Status'] == 'Signed in') | (attendance['Status'] == 'Reserved')]
print(len(attendance))
attendance = attendance.loc[:,['Date', 'Start time', 'End time', 'Description', 'Staff', 'Client ID']]
attendance.to_csv('../Data/processed/attendance.csv', index = False)
