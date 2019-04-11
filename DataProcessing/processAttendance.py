import pandas as pd

attendanceList = []
months = 8
for t in range(months):
    temp = pd.read_excel('../Data/raw/ScheduleAtAGlance Report 10-1-2018 - 10-31-2018.xlsx')
    temp = temp.loc[:,['Date', 'Start time', 'End time', 'Description', 'Staff', 'Client ID', 'Status']]
    attendanceList.append(temp)

attendance = pd.concat(attendanceList)
print(len(attendance))
attendance = attendance.loc[attendance['Status'] == 'Signed in']
print(len(attendance))
attendance = attendance.loc[:,['Date', 'Start time', 'End time', 'Description', 'Staff', 'Client ID']]
attendance.to_csv('../Data/processed/attendance.csv', index = False)
