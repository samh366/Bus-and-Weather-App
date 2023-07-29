import requests
import json
import os

ATCOcode = "3290YYA01059"

url = "https://www.firstbus.co.uk/getNextBus?stop="+ATCOcode

# 67 Southbound code
# ATCO Code = 3290YYA00285  Naptan = 32900285

# 66 Eastbound code
# ATCO Code = 3290YYA01059  Naptan = 32901059


def mins_to_mins_hours(mins):
    """Converts 77 mins to 1h 17 mins as an example"""
    if mins == "Due now":
        return mins
    time = int(mins.rstrip(" mins"))

    if time == 60:
        return "1h 00m"
    elif time < 60:
        return mins
    else:
        hours = time // 60
        minutes = str(time - (hours*60))

        minutes = minutes.zfill(2)

        return f"{hours}h {minutes}m"

icons = [file for file in os.listdir("icons") if os.path.isfile("icons\\" + file)]
print(icons)


response = requests.get(url)
print(response.status_code)
data = response.json()
print(json.dumps(data, indent=4))

busses = data["times"]

if busses == []:
    print("No running departures for today")

else:
    # Print out departures
    for bus in busses:
        print(bus["ServiceNumber"] + " " + mins_to_mins_hours(bus["Due"]))
