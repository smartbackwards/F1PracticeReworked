import pandas as pd
qualiResults = pd.read_csv("f1raceresults2022.csv")
print(qualiResults)
constructorsTable = ['Red Bull', 'Ferrari', 'Mercedes', 'Alpine', 'McLaren','Alfa Romeo','Aston Martin','Haas','Alpha Tauri', 'Williams']
qualiTable = []
for i in range(1074,1097,1):
    if i != 1090:
        qualiTable.append(qualiResults[str(i)].to_list())

results = []
for t in range(10):
    team = []
    for u in range(10):
        team.append(0)
    results.append(team)

qualiRes = []
for quali in qualiTable:
    first = []
    for x in quali:
        if x not in first:
            first.append(x)
    qualiRes.append(first)

for x in qualiRes:
    for i in range(len(x)):
        for j in range(i+1, len(x)):
            winningTeam = x[i]
            losingTeam = x[j]
            winningTeamId=-1
            losingTeamId=-1
            for l in range(len(constructorsTable)):
                if winningTeam==constructorsTable[l]:
                    winningTeamId = l
                if losingTeam==constructorsTable[l]:
                    losingTeamId = l
            results[winningTeamId][losingTeamId]=results[winningTeamId][losingTeamId]+1

for x in results:
    print(x)