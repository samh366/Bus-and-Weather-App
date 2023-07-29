import pygame
from datetime import datetime
import requests
import json
from bs4 import BeautifulSoup

pygame.init()
pygame.font.init()


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        self.running = True

        # Fonts
        self.busNumFont = pygame.font.Font("fonts\\metropolis\\Metropolis-SemiBold.otf", 160)
        self.regularFont = pygame.font.Font("fonts\\metropolis\\Metropolis-Medium.otf", 30)
        self.metro100 = pygame.font.Font("fonts\\metropolis\\Metropolis-SemiBold.otf", 80)

        self.busData = [
            {
                "stop name" : "The Retreat",
                "service" : "66",
                "times" : ["Due Now", "12 Mins", "57 Mins", "1h 15 Mins"]
            }
        ]

        # Manage data about when last requests were sent, and if servers are available
        self.requestData = {
            "daily" : {
                "lastSuccessfulRequest" : None,
                "mostRecentRequest" : None,
                "data" : None
            },

            "weekly" : {
                "lastSuccessfulRequest" : None,
                "mostRecentRequest" : None,
                "data" : None
            },

            "bus" : {
                "lastSuccessfulRequest" : None,
                "mostRecentRequest" : None,
                "data" : None
            },
        }

        self.getWeeklyForecast()


    
    def renderBusInfo(self):
        """Renders info about each bus on the screen"""

        for index, bus in enumerate(self.busData):
            title = self.busNumFont.render(bus["service"], True, (255, 255, 255))
            nextbus = self.regularFont.render("Next Bus:", True, (255, 255, 255))
            time = self.metro100.render(bus["times"][0], True, (255, 255, 255))

            self.screen.blit(title, (20, 20))
            self.screen.blit(nextbus, (33, 170))
            self.screen.blit(time, (30, 220))


    def getDailyForecast(self):
        """Scrapes current weather data from weather.com"""
        url = "https://weather.com/en-GB/weather/today/l/f069b5c5b290a3dd147139a4b9fca15be1ff8c95e8b7de58304c6389e2297e52"
        response = requests.get(url)
        check = datetime.now()
        self.requestData["daily"]["mostRecentRequest"] = check
        
        daily = {}

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Get temperature and weather code
            daily["temperature"] = soup.find("span", {"data-testid" : "TemperatureValue"}).text
            daily["weather"] = soup.find("div", {"data-testid" : "wxPhrase"}).text

            # Wind speed
            windSpeed = soup.find("span", {"data-testid" : "Wind"})
            daily["windspeed"] = windSpeed.findNext("span").findNext("span").text

            # Location
            location = soup.find("div", {"data-testid" : "CurrentConditionsContainer"})
            daily["location"] = location.findNext("h1").text

            self.requestData["daily"]["lastSuccessfulRequest"] = check
            self.requestData["daily"]["data"] = daily
        
        else:
            print("Something went wrong with getting daily data")
            print(response.status_code)
            print(response.content)



    def getWeeklyForecast(self):
        """Requests data about the temperature for the next week"""
        url = "https://api.open-meteo.com/v1/forecast"
        args = {
            "latitude" : 53.9576,
            "longitude" : -1.0827,
            "daily" : "weathercode,temperature_2m_max,temperature_2m_min",
            "timeformat" : "unixtime",
            "timezone" : "Europe/London",
            "forecast_days" : 10
        }

        response = requests.get(url, args)
        check = datetime.now()
        self.requestData["weekly"]["mostRecentRequest"] = check

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

            self.requestData["weekly"]["lastSuccessfulRequest"] = check
            self.requestData["weekly"]["data"] = formatted
            print(formatted)
        
        else:
            print("Something fucked up")
            print(response.status_code)
            print(response.content)





    def main(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            
            self.screen.fill((72, 166, 207))

            self.renderBusInfo()

            pygame.display.flip()
            self.clock.tick(60)



if __name__ == "__main__":
    app = App()
    # app.main()

    pygame.quit()
    quit()