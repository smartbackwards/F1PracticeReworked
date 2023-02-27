import fastf1
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from PIL import ImageFont

fastf1.Cache.enable_cache("cachefolder")
session = fastf1.get_testing_session(2023,1,3) #working session
#session = fastf1.get_session(2022,10,4)
session.load()
#global variables
lapsDataFrame = session.laps
raceControl = session.race_control_messages
drivers = session.drivers
cleanLapTimes = lapsDataFrame["LapTime"].to_list()
cleanLapTimes = [x for x in cleanLapTimes if str(x)!="NaT"]
sessionBest = min(cleanLapTimes)
usedCompounds = [*set(lapsDataFrame['Compound'].to_list())]
testFlag = 0
dryFlag = 0
wetFlag = 0
font = ImageFont.truetype("bahnschrift.ttf",60)
if 'TEST_UNKNOWN' in usedCompounds:
    testFlag = 1
if 'HARD' in usedCompounds or 'MEDIUM' in usedCompounds or 'SOFT' in usedCompounds:
    dryFlag = 1
if 'INTERMEDIATE' in usedCompounds or 'WET' in usedCompounds:
    wetFlag = 1


compoundColors = {
    'SOFT_True': '#FF5F5F',
    'MEDIUM_True': '#F9E75E',
    'HARD_True': '#F0F0F0',
    'INTERMEDIATE_True': '#39B54A',
    'WET_True': '#00AEEF',
    'UNKNOWN_True': '#555555',
    'TEST_UNKNOWN_True': '#555555',


    'SOFT_False': '#933030',
    'MEDIUM_False': '#7c7600',
    'HARD_False': '#999999',
    'INTERMEDIATE_False': '#2b8737',
    'WET_False': '#0078a5',
    'UNKNOWN_False': '#222222',
    'TEST_UNKNOWN_False': '#222222',

    'Session_Best': '#b138dd',
    "Personal_Best": '#4dfbd7'
}
textColors = {
    'SOFT_True': '#000000',
    'MEDIUM_True': '#000000',
    'HARD_True': '#000000',
    'INTERMEDIATE_True': '#000000',
    'WET_True': '#000000',
    'UNKNOWN_True': '#FFFFFF',
    'TEST_UNKNOWN_True': '#FFFFFF',


    'SOFT_False': '#000000',
    'MEDIUM_False': '#000000',
    'HARD_False': '#000000',
    'INTERMEDIATE_False': '#000000',
    'WET_False': '#000000',
    'UNKNOWN_False': '#FFFFFF',
    'TEST_UNKNOWN_False': '#FFFFFF',

    'Session_Best': '#000000',
    'Personal_Best': '#000000'
}

def convert_datetime_to_float(dt):
    return (dt.seconds + dt.microseconds/1000000)/60
def convert_datetime_to_laptime(dt):
    if str(dt)!="NaT":
        if len(str(dt.seconds%60))==2:
            correctSeconds = str(dt.seconds%60)
        else:
            correctSeconds = "0"+str(dt.seconds%60)
        return str(dt.seconds//60)+":"+correctSeconds+"."+str(dt.microseconds)[0:3]
    else:
        return ""
def convert_timestamp_to_float(ts):
    return 60*int(ts.strftime('%H'))+int(ts.strftime('%M'))+int(ts.strftime('%S'))/60+float(ts.strftime('%f'))/60000000
def convert_adjusted_timestamp_to_float(adjts):
    return convert_timestamp_to_float(adjts)-(convert_timestamp_to_float(lapsDataFrame["LapStartDate"].to_list()[0])-convert_datetime_to_float(lapsDataFrame["LapStartTime"].to_list()[0]))
def getDriverLaps(driver_id):
    return lapsDataFrame[lapsDataFrame["DriverNumber"]==driver_id]    
def getTeamList():
    teamlist = []
    for driver in drivers:
        if session.get_driver(driver).TeamName not in teamlist:
            teamlist.append(session.get_driver(driver).TeamName)
    return teamlist
def getDriverList(teamlist):
    driverlist = []
    for team in teamlist:
        for driver in drivers:
            if session.get_driver(driver).TeamName==team:
                driverlist.append(driver)
    return driverlist

def get_lap_dictionaries(lap_dataframe):
    laps = []

    pit_out_time = lap_dataframe["PitOutTime"].to_list()
    pit_in_time = lap_dataframe["PitInTime"].to_list()
    time = lap_dataframe["Time"].to_list()
    lap_start_time = lap_dataframe["LapStartTime"].to_list()

    lap_time = lap_dataframe["LapTime"].to_list()
    compound = lap_dataframe["Compound"].to_list()
    freshness = lap_dataframe["FreshTyre"].to_list()
    clean_lap_times = [x for x in lap_time if str(x)!="NaT"]
    try:
        personalBest = min(clean_lap_times)
    except:
        True
    for i in range(len(pit_out_time)):
        lap_dictionary = {}
        if str(pit_out_time[i]) != 'NaT':
            start_time = convert_datetime_to_float(pit_out_time[i])
        else:
            start_time = convert_datetime_to_float(lap_start_time[i])
        if str(pit_in_time[i]) != 'NaT':
            end_time = convert_datetime_to_float(pit_in_time[i])
        else:
            end_time = convert_datetime_to_float(time[i])
        lap_dictionary["start_time"] = start_time
        lap_dictionary["end_time"] = end_time
        lap_dictionary["lap_time"] = convert_datetime_to_laptime(lap_time[i])
        if lap_time[i]==sessionBest:
            lap_dictionary["tyre"] = "Session_Best"
        elif lap_time[i]==personalBest:
            lap_dictionary["tyre"] = "Personal_Best"
        elif str(compound[i])!='nan':   
            lap_dictionary["tyre"] = str(compound[i])+"_"+str(freshness[i])
        else:
            lap_dictionary["tyre"] = 'UNKNOWN_False'
        laps.append(lap_dictionary)

    return laps

rcmtimes = raceControl["Time"].to_list()
rcmmessages = raceControl["Message"].to_list()
rcmstatus = raceControl["Status"].to_list()
rcmcategory = raceControl["Category"].to_list()
rcmflags = raceControl["Flag"].to_list()
def getFirstGreenFlagTime():
    for i in range(len(rcmtimes)):
        if rcmflags[i]=="GREEN":
            return convert_adjusted_timestamp_to_float(rcmtimes[i])
def getSafetyCarPeriods():
    sc_begin = []
    sc_ending = []
    sc = False
    for i in range(len(rcmtimes)):
        if (not sc) and rcmcategory[i]=="SafetyCar" and rcmstatus[i]=="DEPLOYED":
            sc = True
            sc_begin.append(convert_adjusted_timestamp_to_float(rcmtimes[i]))
        if sc and (rcmmessages[i] =="RED FLAG" or rcmmessages[i]=="SESSION WILL NOT BE RESUMED" or rcmmessages[i]=="TRACK CLEAR" or rcmflags[i] =="CHEQUERED"):
            sc = False
            sc_ending.append(convert_adjusted_timestamp_to_float(rcmtimes[i]))
    if len(sc_begin) == len(sc_ending):
        return [sc_begin,sc_ending]
    else:
        print("[SAFETY CAR] UNEVEN BEGINNINGS AND ENDINGS")
        return [[],[]]
def getRedFlagPeriods():
    rf_begin = []
    rf_ending = []
    rf = False
    for i in range(len(rcmtimes)):
        if (not rf) and rcmcategory[i]=="Flag" and rcmflags[i]=="RED":
            rf = True
            rf_begin.append(convert_adjusted_timestamp_to_float(rcmtimes[i]))
        if rf and (rcmflags[i] =="GREEN" or rcmflags[i] =="CHEQUERED" or rcmmessages[i]=="SESSION WILL NOT BE RESUMED" or rcmmessages[i]=="AIR TEMPERATURE 1 HOUR BEFORE THE SESSION = 31.1 DEGREES"):
            rf = False
            rf_ending.append(convert_adjusted_timestamp_to_float(rcmtimes[i]))
    rf_ending.append(convert_adjusted_timestamp_to_float(rcmtimes[len(rcmtimes)-1]))
    print(rf_begin, rf_ending)
    if len(rf_begin) == len(rf_ending):
        return [rf_begin,rf_ending]
    else:
        print("[RED FLAG] UNEVEN BEGINNINGS AND ENDINGS")
        return [[],[]]
def getLastChequeredFlag():
    for i in range(len(rcmflags)):
        if rcmflags[i]=="CHEQUERED":
            fl = convert_adjusted_timestamp_to_float(rcmtimes[i])
    return fl
def create_testing_graphic(drivers, y_limit):
    plt.rcParams["figure.figsize"] = [30,20] #[40,20] for 10 teams [30,20] for less
    fig, ax = plt.subplots()
    ax.set_facecolor("#d9d9d9")
    fig.set_facecolor("#13151d")
    plt.ylim((y_limit[0]-y_limit[1],0))
    #title = session.event["EventName"]+" 2022 "+session.name
    title = "PRE-SEASON TESTING DAY 3 - PM SESSION HOURS 3 & 4"
    #plt.title(title.upper(), fontfamily="Bahnschrift", size = 40, color="white", pad=15)
    for i in range (len(drivers)):
        for lap in get_lap_dictionaries(getDriverLaps(drivers[i])):
            if lap['end_time']>270:
                plt.bar(i, lap['end_time']-lap['start_time'],0.75, lap['start_time']-y_limit[1], color = compoundColors[lap['tyre']], edgecolor = "black")
                plt.text(i, lap['end_time']-y_limit[1]-(lap['end_time']-lap['start_time'])/2,lap['lap_time'],fontsize=15, verticalalignment='center',horizontalalignment='center',fontfamily='Arial', color=textColors[lap['tyre']])
    #adding red flags
    driverCounter = i
    redflagbegin = getRedFlagPeriods()[0]
    redflagend = getRedFlagPeriods()[1]
    for i in range(len(redflagbegin)):
        rect = plt.Rectangle((-0.5,redflagend[i]-y_limit[1]),driverCounter+1,redflagbegin[i]-redflagend[i],color = "r", alpha = 0.3)
        ax.add_patch(rect)
    scbegin = getSafetyCarPeriods()[0]
    scend = getSafetyCarPeriods()[1]
    for i in range(len(scbegin)):
        rect = plt.Rectangle((-0.5,scend[i]-y_limit[1]),driverCounter+1,scbegin[i]-scend[i],color = "y", alpha = 0.3)
        ax.add_patch(rect)
    tick = []
    for i in range(len(drivers)):
        tick.append(session.get_driver(drivers[i]).LastName.upper())
    ax.set_xticks([x for x in range(len(drivers))])
    ax.set_xticklabels(tick, fontfamily="Bahnschrift", size = 20, color="white")
    ax.tick_params(axis='x',pad=10)
    ax.tick_params(axis='y', colors='white', size = 10)
    plt.yticks(fontsize=15,fontfamily="Bahnschrift")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    try:
        plt.axhline(y=getLastChequeredFlag()-y_limit[1], color = "black", linestyle = "--")
    except:
        1==1
    plt.savefig(title+" "+drivers[0],bbox_inches='tight',pad_inches=1)
    background = Image.open(title+" "+drivers[0]+".png")
    fg = ""
    if testFlag == 1:
        fg = "testing.png"
    elif dryFlag == 1 and wetFlag == 0:
        fg = "dry.png"
    elif dryFlag == 0 and wetFlag == 1:
        fg = "wet.png"
    elif dryFlag == 1 and wetFlag == 1:
        fg = "wetanddry.png"
    foreground = Image.open(fg)
    draw = ImageDraw.Draw(background)
    #background.paste(foreground, (0,0), foreground)
    draw.text((1284-font.getlength(title.upper())/2,20),title.upper(),font=font)
    #background.save(title+" "+drivers[0]+".png")
    background.save("testing3PM1.png")
#main...


#topdrivers = getDriverList(['Red Bull Racing', 'Ferrari', 'Mercedes', 'Alpine', 'McLaren'])
#botdrivers = getDriverList(['Alfa Romeo', 'Aston Martin', 'Haas F1 Team', 'AlphaTauri', 'Williams'])
create_testing_graphic(['11','55','44','31','4','77','14','20','22','23'],(getFirstGreenFlagTime()+455+120,getFirstGreenFlagTime()+315+120))
#['1','55','44','31','4','24','14','20','22','2']