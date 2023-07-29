import requests
from datetime import datetime
import json

# OLD AND RUBBISH, ONLY REPORTS TIMETABLED TIMES

appID = "e059e90b"
appKey = "c232abe4a641cf71661d28ba508e8f24"
ATCOcode = "3290YYA01059"

url = "https://transportapi.com/v3/uk/bus/stop_timetables/{}.json".format(
    ATCOcode
)


appID = "75da7e19"
appKey = "8a756a1369a55907a33042def6008ec8"

args = {"app_id" : appID, "app_key" : appKey, "limit" : 20, "live" : "true", "group" : "false"}

args = {"stop" : ATCOcode}




# 67 Southbound code
# ATCO Code = 3290YYA00285  Naptan = 32900285

# 66 Eastbound code
# ATCO Code = 3290YYA01059  Naptan = 32901059

def timeToCountDown(time):
    # Takes in a time of format HH:MM and converts it to how long away that time is in minutes
    now = datetime.now()

    timeObject = datetime.strptime(time, r"%H:%M")

    timeUntil = timeObject - now

    # Format nicely 
    if timeUntil.seconds//3600 > 0:
        return "{} hour {} min".format(timeUntil.seconds//3600, (timeUntil.seconds - (timeUntil.seconds//3600)*3600)//60)
    elif timeUntil.seconds//60 == 0:
        return "Due"
    else:
        return "{} min".format(timeUntil.seconds//60)


# Doesn't pull live bus data, just gets shit timetable data

response = requests.get(url, args)
print(response.status_code)
# Have data
data = response.json()
print(json.dumps(data, indent=4))

busses = data["departures"]["all"]

if busses == []:
    print("No running departures for today")

else:
    # Print out departures
    for bus in busses:
        print(bus["line"] + " " + timeToCountDown(bus["best_departure_estimate"]))
