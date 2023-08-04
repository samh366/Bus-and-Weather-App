import os
import time
from datetime import datetime
from threading import Thread

import pygame
import requests
from bs4 import BeautifulSoup

pygame.init()
pygame.font.init()

from classes.weather_manager import WeatherManager
from classes.cloud import Cloud
from classes.font_manager import FontManager
from classes.utils import mins_to_mins_hours, smartResize, loadConfig

### DISABLES FLASHING IMAGES ###
DISABLELIGHTNING = False
################################

# Screen size
RES = (1280, 720)
WIDTH, HEIGHT = RES

# Colours
WHITE = (255, 255, 255)
GREY = (175, 175, 175)
BLUE = (72, 166, 207)

# Requests timeout
TIMEOUT = 10

# Rain credit
# 4kmotionworld


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.running = True
        self.requesting = False
        self.status = ""


        # Loads ATCO codes to request data from
        # Loads which bus to get from each stop
        # Additionally, loads default information about the bus service data if it cannot be grabbed
        # And loads the weather.com url code to get area weather data from

        self.config = loadConfig("config.txt")

        # # ATCO Codes
        # self.ATCOCode1 = "3290YYA01059" # 66
        # self.ATCOCode2 = "3290YYA00285" # 67
        # # Filter the busses you want from each stop
        # self.stopFilters = ["66", "67"]

        # Font manager
        self.font = FontManager(RES)

        # Data
        self.apiData = {
                    "daily" : {
                        "lastSuccessfulRequest" : None,
                        "mostRecentRequest" : None,
                        "interval" : 60*5,
                        "data" : None
                    },

                    "weekly" : {
                        "lastSuccessfulRequest" : None,
                        "mostRecentRequest" : None,
                        "interval" : 60*60,
                        "data" : None
                    },

                    "bus" : {
                        "lastSuccessfulRequest" : None,
                        "mostRecentRequest" : None,
                        "interval" : 60,
                        "data" : [{}, {}]
                    },
                }
        
        # # Default bus data, used to display the service and destination if they cannot be fetched
        # self.defaultBusData = [
        #     {"service" : "66", "destination" : "York Sport Village"},
        #     {"service" : "67", "destination" : "York Sport Village"}
        # ]


        # Clouds
        Cloud.width = WIDTH

        # Debug weather info
        self.debugWeatherCodes = ["sunny", "partly-sunny",
                                  "cloudy", "rain",
                                  "fog", "snow",
                                  "clear", "mostly-clear"]
        
        # Weather manager
        self.weather = WeatherManager(self.screen, RES, DISABLELIGHTNING)

        # Static gui
        self.staticGUI = self.generateStaticGui()

        # Non-static gui
        self.nonStaticGUI = self.generateNonStaticGui()
        self.updateNonStaticGUI = False

    
    def iconGetter(self, weather):
        """Returns the correct icon based on a weather type"""
        # Get icons
        icons = [file for file in os.listdir("icons") if os.path.isfile("icons\\" + file)]

        fileName = weather.replace(" ", "-") + ".png"

        if fileName in icons:
            return pygame.image.load("icons\\" + fileName)
        
        # Add other mappings
        if "showers" in weather:
            return pygame.image.load("icons\\rain.png")
        if "storm" in weather:
            return pygame.image.load("icons\\lightning.png")
        if "snow" in weather or "hail" in weather:
            return pygame.image.load("icons\\snow.png")
        if "wind" in weather or "tornado" in weather:
            return pygame.image.load("icons\\wind.png")

        return pygame.image.load("icons\\cloudy.png")
    

    def generateStaticGui(self):
        """Generates the unchanging elements of the gui"""
        static = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)

        # Draw 2 lines
        for i in range(1, 3):
            pygame.draw.line(static, WHITE, (i*(WIDTH//3), HEIGHT*0.05), (i*(WIDTH//3), HEIGHT*0.95))

        # Generate 3 sets of 2 lines
        length = 100
        height = 350
        yspacing = 120
        for i in range(1, 6, 2):
            pygame.draw.line(static, WHITE, (i*(WIDTH//6)-length//2, height - yspacing//2), (i*(WIDTH//6)+length//2, height - yspacing//2))
            pygame.draw.line(static, WHITE, (i*(WIDTH//6)-length//2, height + yspacing//2), (i*(WIDTH//6)+length//2, height + yspacing//2))

        
        return static

    
    def generateNonStaticGui(self):
        """
        Render elements of the display that may change e.g. bus times and weather data
        Does not render the weather images in the background
        """

        nonStatic = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)

        # Bus timetable data

        for index, bus in enumerate(self.apiData["bus"]["data"]):
            if bus != {}:
                # Check for missing values
                if bus["destination"] == "":
                    bus["destination"] = self.config["default_service_data"][index]["destination"]


                # Calc x value to align text to
                centre_x = (2*index + 1) * (WIDTH//6)
                # Service names
                self.font.renderAndBlit(self.config["stop_filters"][index], self.font.busNum, nonStatic, (centre_x, 110))
                # Subtitle
                self.font.renderAndBlit(bus["destination"], self.font.subtitle, nonStatic, (centre_x, 188))
                # Stop name
                self.font.renderAndBlit(bus["stop name"], self.font.stopName, nonStatic, (centre_x, 240))
                # Next time
                if bus["times"] != []:
                    self.font.renderAndBlit(bus["times"][0], self.font.nextTime, nonStatic, (centre_x, 354))
                else:
                    self.font.renderAndBlit("Not Running", self.font.nextTime, nonStatic, (centre_x, 354))
                # Next departures subtitle
                self.font.renderAndBlit("Next Departures", self.font.subtitle, nonStatic, (centre_x, 450))

                # List next departures
                for j, time in enumerate(bus["times"][1:4]):
                    self.font.renderAndBlit(time, self.font.nextTimeList, nonStatic, (centre_x, 500 + j*67))


        # Current day weather information

        centre_x = 5*(WIDTH//6)

        if self.apiData["daily"]["data"] != None:
            data = self.apiData["daily"]["data"]
            # Temp
            self.font.renderAndBlit(data["temperature"], self.font.temperature, nonStatic, (centre_x+75, 110))
            # Icon
            image = self.iconGetter(data["weather"].lower().replace(" ", "-")).convert_alpha()
            image = smartResize(image, (130, 130), smooth=True)
            self.font.centreAndBlitImage(image, nonStatic, (centre_x-87, 100))
            # Location
            self.font.renderAndBlit(data["location"], self.font.subtitle, nonStatic, (centre_x, 188))
            # Time
            # Blitted every frame in main
            # Weather
            self.font.renderAndBlit(data["weather"], self.font.weather, nonStatic, (centre_x, 337))
            # Wind speed + wind speed
            self.font.renderAndBlit("Wind: " + data["windspeed"] + "mph" + " "*7 + "Rain: " + data["rain chance"],
                                    self.font.smallweatherdata, nonStatic, (centre_x, 385))
        
        # Weather forecast for the next week
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        if self.apiData["weekly"]["data"] != None:
            for index, day in enumerate(self.apiData["weekly"]["data"]):
                # Day
                self.font.renderAndBlit(weekdays[day[0]], self.font.forecast, nonStatic, (centre_x-160, 415+(index*40)), centre=False)

                # Highest temp
                self.font.renderAndBlit(str(round(day[2])), self.font.forecast, nonStatic, (centre_x+90, 415+(index*40)), centre=False)

                # Lowest temp
                self.font.renderAndBlit(str(round(day[3])), self.font.forecast, nonStatic, (centre_x+135, 415+(index*40)), centre=False, color=GREY, mode=pygame.BLEND_RGBA_MAX)

        return nonStatic
    


    # Data getters
    def getBusData(self):
        self.requesting = True

        data = [{}, {}]

        for index, code in enumerate([self.config["atco_code1"], self.config["atco_code2"]]):
            self.status = "Fetching bus time data for stop {}...".format(str(index+1))
            busData = {}
            url = "https://www.firstbus.co.uk/getNextBus"
            args = {"stop" : code}

            response = requests.get(url, args, timeout=TIMEOUT)
            print(f"Request for stop [{code}] data made")

            check = datetime.now()
            self.apiData["bus"]["mostRecentRequest"] = check

            if response.status_code == 200:
                self.apiData["bus"]["lastSuccessfulRequest"] = check
                responseData = response.json()
                busData["stop name"] = responseData["stop_name"]
                busData["destination"] = ""
                busData["times"] = []
                
                if responseData["times"] != []:
                    for bus in responseData["times"]:
                        if bus["ServiceNumber"] == self.config["stop_filters"][index]:
                            busData["times"].append(mins_to_mins_hours(bus["Due"]))
                            busData["destination"] = bus["Destination"]
                
                data[index] = busData
            
            else:
                print(f"Something went wrong with getting bus stop {code} data")
                print(response.status_code)
                print(response.content)
            
            self.apiData["bus"]["data"][index] = data[index]
            self.updateNonStaticGUI = True
            if index == 0:
                self.status = "Waiting to ping..."
                time.sleep(3)


        self.requesting = False
        self.status = ""
        



    def getDailyForecast(self):
        """Scrapes current weather data from weather.com"""
        self.requesting = True
        self.status = "Fetching daily weather data..."
        url = "https://weather.com/en-GB/weather/today/l/" + self.config["weather.com_code"]
        response = requests.get(url, timeout=TIMEOUT)
        print("Request for daily data made")
        check = datetime.now()
        self.apiData["daily"]["mostRecentRequest"] = check
        
        daily = {}

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Get temperature and weather code
            daily["temperature"] = soup.find("span", {"data-testid" : "TemperatureValue"}).text
            daily["weather"] = soup.find("div", {"data-testid" : "wxPhrase"}).text

            # Wind speed
            windSpeed = soup.find("span", {"data-testid" : "Wind"})
            daily["windspeed"] = windSpeed.findNext("span").findNext("span").text

            # Rain chance
            rainChance = soup.find("section", {"aria-label" : "Hourly Forecast"})
            for i in range(4):
                rainChance = rainChance.findNext("span")
            
            daily["rain chance"] = rainChance.text.lstrip("Chance of Rain")

            # Location
            location = soup.find("div", {"data-testid" : "CurrentConditionsContainer"})
            daily["location"] = location.findNext("h1").text

            self.apiData["daily"]["lastSuccessfulRequest"] = check
            self.apiData["daily"]["data"] = daily

            self.updateNonStaticGUI = True
            self.weather.setWeather(self.apiData["daily"]["data"]["weather"].lower().replace(" ", "-"))
        
        else:
            print("Something went wrong with getting daily data")
            print(response.status_code)
            print(response.content)
        
        self.requesting = False
        self.status = ""

    

    def getWeeklyForecast(self):
            """Requests data about the temperature for the next week"""
            url = "https://api.open-meteo.com/v1/forecast"
            args = {
                "latitude" : 53.9576,
                "longitude" : -1.0827,
                "daily" : "weathercode,temperature_2m_max,temperature_2m_min",
                "timeformat" : "unixtime",
                "timezone" : "Europe/London",
                "forecast_days" : 8
            }

            self.requesting = True
            self.status = "Fetching weekly weather data..."

            response = requests.get(url, args, timeout=TIMEOUT)
            print("Request for weekly data made")
            check = datetime.now()
            self.apiData["weekly"]["mostRecentRequest"] = check

            if response.status_code == 200:
                weatherDat = response.json()

                formatted = []

                for index, time in enumerate(weatherDat["daily"]["time"][1:]):
                    day = []
                    # Skip first day
                    index += 1
                    time = datetime.fromtimestamp(float(time))
                    day.append(time.weekday())
                    day.append(weatherDat["daily"]["weathercode"][index])
                    day.append(weatherDat["daily"]["temperature_2m_max"][index])
                    day.append(weatherDat["daily"]["temperature_2m_min"][index])

                    formatted.append(day)
                
                self.weeklyWeather = formatted

                self.apiData["weekly"]["lastSuccessfulRequest"] = check
                self.apiData["weekly"]["data"] = formatted

                self.updateNonStaticGUI = True

            
            else:
                print("Something fucked up")
                print(response.status_code)
                print(response.content)

            self.requesting = False
            self.status = ""

    
    def dataCheck(self):
        """Checks for missing or expired data, if so requests it"""
        now = datetime.now()

        # Check bus data
        dat = self.apiData["bus"]
        if dat["data"] == [{}, {}] or dat["mostRecentRequest"] == None or (now - dat["mostRecentRequest"]).total_seconds() >= dat["interval"]:
            # Request data in a new thread
            self.requesting = True
            thread = Thread(target = self.getBusData, daemon=True)
            thread.start()
            return

        # Check Daily temp data
        dat = self.apiData["daily"]
        if dat["data"] == None or (now - dat["mostRecentRequest"]).total_seconds() >= dat["interval"]:
            self.requesting = True
            thread = Thread(target = self.getDailyForecast, daemon=True)
            thread.start()
            return
    
        # Check weekly temp data
        dat = self.apiData["weekly"]
        if dat["data"] == None or (now - dat["mostRecentRequest"]).total_seconds() >= dat["interval"]:
            self.requesting = True
            thread = Thread(target = self.getWeeklyForecast, daemon=True)
            thread.start()
            return



    def main(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                    # Good for debugging
                    if event.key == pygame.K_SPACE:
                        self.weather.randomise()
                    
                    if event.key == pygame.K_r:
                        self.weather.setWeather(self.apiData["daily"]["data"]["weather"].lower().replace(" ", "-"))

                    if event.key == pygame.K_RETURN:
                        self.apiData["bus"]["mostRecentRequest"] = None

            # Check data
            if not self.requesting:
                self.dataCheck()
            
            # Dynamic weather
            self.weather.renderWeather()

            # Static and non-static GUI
            self.screen.blit(self.staticGUI, (0, 0))

            if self.updateNonStaticGUI == True:
                self.nonStaticGUI = self.generateNonStaticGui()
                self.updateNonStaticGUI = False

            self.screen.blit(self.nonStaticGUI, (0, 0))

            # Update time
            time = datetime.now().strftime("%I:%M %p").lstrip("0")
            self.font.renderAndBlit(time, self.font.stopName, self.screen, (5*(WIDTH//6), 243))

            # Blit status
            self.font.renderAndBlit(self.status, self.font.statusFont, self.screen, (WIDTH//2, HEIGHT*0.985))


            pygame.display.flip()
            self.clock.tick(30)



if __name__ == "__main__":
    app = App()
    app.main()

    pygame.quit()
    quit()