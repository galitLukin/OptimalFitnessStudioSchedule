import pandas as pd
import glob

import cleaning

attendanceList = []
files = glob.glob('../Data/raw/' + "/*.xlsx")

for f in files:
    temp = pd.read_excel(f)
    temp = temp.loc[:,['Date', 'Start time', 'Description', 'Staff', 'Client ID', 'Status']]
    attendanceList.append(temp)

attendance = pd.concat(attendanceList)

#take only users that arrived
attendance = attendance.loc[(attendance['Status'] == 'Signed in') | (attendance['Status'] == 'Reserved')]
attendance = attendance.loc[:,['Date', 'Start time', 'Description', 'Staff', 'Client ID']]
attendance.to_csv('../Data/processed/attendance.csv', index = False)

#general - to see if to filter out dates
perDate = attendance.loc[:,['Date','Start time','Client ID']]
perDate = perDate.groupby(['Date', 'Start time']).count().reset_index()
perDate = perDate.groupby('Date').mean().reset_index()
perDate.to_csv('../Data/processed/avgPerClassPerDate.csv', index = False)

# attendance distribution over class types
perClassType = attendance
perClassType.Description = perClassType.Description.apply(lambda c: cleaning.currectClasses(c))
perClassType = perClassType.loc[perClassType.Description != "Filter"]
perClassType = perClassType.loc[:,['Description','Date','Start time','Client ID']].drop_duplicates()
resClassType = perClassType.groupby(['Description','Date','Start time']).count().reset_index()
resClassType = resClassType.loc[:,['Description','Client ID']]
resClassType = resClassType.groupby('Description')['Client ID'].apply(list)
resClassType = resClassType.to_frame().reset_index()
resClassType.to_csv('../Data/processed/perClassType.csv', index = False)

# attendance distribution over instructors
perInstructor = attendance
perInstructor.Staff = perInstructor.Staff.apply(lambda instructor: cleaning.filterInstructors(instructor))
perInstructor = perInstructor.loc[perInstructor.Staff != "Filter"]
perInstructor = perInstructor.loc[:,['Date','Start time','Staff','Client ID']].drop_duplicates()
resInstructor = perInstructor.groupby(['Staff','Date','Start time']).count().reset_index()
resInstructor = resInstructor.loc[:,['Staff','Client ID']]
resInstructor = resInstructor.groupby('Staff')['Client ID'].apply(list)
resInstructor = resInstructor.to_frame().reset_index()
resInstructor.to_csv('../Data/processed/perIntructor.csv', index = False)

# attendance distribution per day
perDay = attendance
perDay = perDay.loc[:,['Date','Start time','Client ID']].drop_duplicates()
resDay = perDay.groupby('Date').count().reset_index()
resDay['DayOfWeek'] = resDay['Date'].dt.day_name()
resDay = resDay.loc[:,['DayOfWeek','Client ID']]
resDay = resDay.groupby('DayOfWeek')['Client ID'].apply(list)
resDay = resDay.to_frame().reset_index()
resDay.to_csv('../Data/processed/perDay.csv', index = False)

# attendance distriution per hour
perHour = attendance
perHour = perHour.loc[:,['Date','Start time','Client ID']].drop_duplicates()
resHour = perHour.groupby(['Date','Start time']).count().reset_index()
resHour = resHour.groupby('Start time')['Client ID'].apply(list)
resHour = resHour.to_frame().reset_index()
resHour.to_csv('../Data/processed/perHour.csv', index = False)
