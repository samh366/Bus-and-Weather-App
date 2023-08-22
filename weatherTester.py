import os
import random

import pygame

from classes.weather_manager import WeatherManager

pygame.init()
pygame.font.init()


## To be used to test the weather features without calling the apis


#### DISABLES FLASHING IMAGES ####
DISABLELIGHTNING = False
##################################

RES = (1280, 720)
WIDTH, HEIGHT = RES

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.running = True
        
        self.weather = WeatherManager(self.screen, RES)

        self.weather.setWeather("clear")

        self.debugWeatherCodes = ["sunny", "partly-sunny",
                                  "cloudy", "rain",
                                  "fog", "snow",
                                  "clear", "mostly-clear"]



    def main(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    
                    if event.key == pygame.K_SPACE:
                        self.weather.setWeather(random.choice(self.debugWeatherCodes))

 
            self.weather.renderWeather()


            pygame.display.flip()
            self.clock.tick(30)




if __name__ == "__main__":
    app = App()
    app.main()

    pygame.quit()
    quit()