import pandas as pd
qualiResults = pd.read_csv("normalpoints.csv")
qualiTable = []
constructorsTable = ['Red Bull', 'Ferrari', 'Mercedes', 'Alpine', 'McLaren','Alfa Romeo','Aston Martin','Haas','Alpha Tauri', 'Williams']
for i in range(1074,1097,1):
    if i != 1090:
        qualiTable.append(qualiResults[str(i)].to_list())
results = []
for t in range(10):
    team = []
    for u in range(10):
        team.append(0)
    results.append(team)

for x in qualiTable:
    for i in range(len(x)):
        for j in range(10):
            if x[i]>x[j]:
                results[i][j]=results[i][j]+1
            


for x in results:
    print(x)