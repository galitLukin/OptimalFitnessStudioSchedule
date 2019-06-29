import pandas as pd

df = pd.DataFrame(index=range(20),columns=['Diversity','Supply','MinDemand','Classes','Instructors'])
df.Diversity = [0]*5+[4]*5+[8]*5+[12]*5
df.Supply = [0,5,10,15,20]+[0,5,10,15,20]+[0,5,10,15,20]+[0,5,10,15,20]
df.MinDemand = [693.306,693.306,666.237,571.019,449.721,681.695,681.695,671.982,563.359,466.58,658.555,658.555,658.555,583.291,473.703,639.767,639.767,639.767,601.446,480.89]
df.Classes = [42,42,39,31,24,42,42,41,31,25,42,42,42,34,26,42,42,42,39,29]
df.Instructors = [16,16,17,14,14,22,22,22,18,16,26,26,26,22,18,28,28,28,28,23]
df.to_csv("../Data/output/options.csv")