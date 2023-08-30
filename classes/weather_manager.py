import datetime
import os
import random
from os.path import join

import pygame

from classes.cloud import Cloud
from classes.utils import smartResize
from classes.utils import getSmartScale

WHITE = (255, 255, 255)
GREY = (175, 175, 175)
BLUE = (72, 166, 207)
BLUEGREY = (77, 111, 125)
DARKBLUE = (0, 15, 48)


class WeatherManager:
    def __init__(self, screen, RES, DISABLELIGHTNING=False, DISABLEANIMATIONS=False):
        """Generates weather based on the given conditions"""
        self.screen = screen
        self.activeWeather = self.mostlySunny
        self.loading = False

        self.DISABLELIGHTNING = DISABLELIGHTNING
        self.DISABLEANIMATIONS = DISABLEANIMATIONS
        self.RES = RES
        self.WIDTH, self.HEIGHT = RES

        self.clouds = {
            "cloudy" : [
                Cloud(join("weather", "clouds", "big_cloud.png"), 220, (500, 500), pos=(random.randint(800, 1000), random.randint(-30, 20))),
                Cloud(join("weather", "clouds", "big_cloud.png"), 220, (500, 500), pos=(random.randint(-300, 400), random.randint(-30, 20)))
            ],
            "mostly sunny" : [
                Cloud(join("weather", "clouds", "cloud3.png"), opacity=180, size=(400, 400), pos=(random.randint(800, 1000), random.randint(-30, 20))),
                Cloud(join("weather", "clouds", "cloud4.png"), 180, (300, 300), pos=(random.randint(-300, 400), random.randint(-30, 20)))
            ],
            "mostly clear" : [
                Cloud(join("weather", "clouds", "dark_cloud1.png"), 180, size=(400, 400), pos=(random.randint(800, 1000), random.randint(-30, 20))),
                Cloud(join("weather", "clouds", "dark_cloud2.png"), 180, size=(300, 300), pos=(random.randint(-300, 400), random.randint(-30, 20)))
            ]
        }

        self.clouds["cloudy"][1].flip()

        self.gradients = {
            "cloudy" : self.generateGradient(self.RES, (100, 100, 100), 230, 130, self.HEIGHT*1.2),
            "rain" : self.generateGradient(self.RES, (50, 50, 50), 255, 180, self.HEIGHT*1.3),
            "mostly-sunny" : self.generateGradient(self.RES, (255, 244, 191), 40, 0, self.HEIGHT*1.1),
            "clear" : self.generateGradient(self.RES, (0, 0, 0), 100, 0, self.HEIGHT*0.9),
            "stars" : self.generateGradient(self.RES, (0, 0, 0), 220, 0, self.HEIGHT*0.8),
            "snow" : self.generateGradient(self.RES, (100, 100, 100), 255, 180, self.HEIGHT*1.3),
            "lightning" : self.generateGradient(self.RES, (75, 75, 75), 255, 180, self.HEIGHT*1.3),
            "fog" : self.generateGradient(self.RES, (120, 120, 120), 230, 130, self.HEIGHT*1.2)
        }

        self.lensFlare = self.getImageWithOpacity(join("weather", "sunny", "lens flare.png"), opacity=150)
        self.stars = self.getImageWithOpacity(join("weather", "stars", "stars.png"), opacity=150)
        self.fogOverlay = self.getImageWithOpacity(join("weather", "fog", random.choice(["fog1.jpg", "fog2.jpg"])), opacity=100)
        self.rainDrops = self.getImageWithOpacity(join("weather", "raindrops", "raindrops.jpg"), opacity=180, resize=True)
        
        # Position info for specific overlays
        self.starPos = 0
        self.fogPos = 0


        # Moving overlay
        self.movingOverlay = []
        self.movingIndex = 0
        self.loadedOverlay = None

        self.flashes = [
            [2, 1, 2],
            [1, 2, 1],
            [1, 2, 1, 2, 1],
            [2, 3, 1, 3, 1]
        ]

        # Stores whether the screen is flashing, and is so how long for
        self.flashing = [False, 0]
        # Stores how many frames of flashing/non-flashing are left in the lightning animation
        self.currentFlash = []


    def setWeather(self, weathercode):
        """Sets the function to be used to display the weather and loads any needed overlays"""

        weathercode = weathercode.lower().replace(" ", "-")
        hour = datetime.datetime.now().hour
        night = True
        if hour > 5 and hour < 22:
            night = False

        # Not the most glamorus way to do things
        # But it works and it's easy to understand ¯\_(ツ)_/¯

        if weathercode == "cloudy" or weathercode == "mostly-cloudy":
            self.activeWeather = self.cloudy
        elif "rain" in weathercode or "shower" in weathercode:
            self.loadMovingOverlay(join("weather", "rain"), 150)
            self.activeWeather = self.rain
        elif weathercode == "mostly-sunny":
            self.activeWeather = self.mostlySunny
        elif weathercode == "sunny":
            self.activeWeather = self.sunny
        elif weathercode == "clear":
            self.activeWeather = self.clear
        elif weathercode == "mostly-clear" or (weathercode == "mostly-cloudy" and night == True):
            self.activeWeather = self.mostlyClear
        elif weathercode == "snow":
            self.loadMovingOverlay(join("weather", "snow"), 150)
            self.activeWeather = self.snow
        elif weathercode == "storm":
            self.loadMovingOverlay(join("weather", "rain"), 150)
            self.activeWeather = self.storm
        elif weathercode == "fog":
            self.activeWeather = self.fog
        
        else:
            self.activeWeather = self.mostlySunny


    def renderWeather(self):
        """Renders the active weather state to the screen, to be called every frame"""
        self.activeWeather()


    def randomise(self):
        """Useful for debugging and testing"""
        codes = ["sunny", "partly-sunny",
                "cloudy", "rain",
                "fog", "snow",
                "clear", "mostly-clear", "storm"]
        self.setWeather(random.choice(codes))

    
    # Snow
    def snow(self):
        self.screen.fill(BLUEGREY)
        self.screen.blit(self.gradients["snow"], (0, 0))
        self.screen.blit(self.getMovingOverlay(), (0, 0), special_flags=pygame.BLEND_RGB_ADD)


    # Mostly clear
    def mostlyClear(self):
        self.clear()

        # Clouds
        for cloud in self.clouds["mostly clear"]:
            cloud.render(self.screen)
            if not self.DISABLEANIMATIONS:
                cloud.advance()

    
    # Clear
    def clear(self):
        # A gradient of stars that slowly moves downward
        self.screen.fill(DARKBLUE)
        self.screen.blit(self.gradients["clear"], (0, 0))

        starSurface = pygame.surface.Surface(self.RES)
        starSurface.blit(self.stars, (0, round(self.starPos)))
        starSurface.blit(self.stars, (0, round(self.starPos)-self.HEIGHT))

        if not self.DISABLEANIMATIONS:
            self.starPos += 0.25
            if self.starPos > self.HEIGHT:
                self.starPos = 0

        # Add some gradient opacity 
        starSurface.blit(pygame.transform.flip(self.gradients["stars"], flip_x=False, flip_y=True), (0, 0))

        self.screen.blit(starSurface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        

    # Sunny
    def sunny(self):
        self.screen.fill(BLUE)
        self.screen.blit(self.gradients["mostly-sunny"], (0, 0))
        self.screen.blit(self.lensFlare, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


    # Mostly sunny
    def mostlySunny(self):
        self.screen.fill(BLUE)
        #self.screen.blit(self.gradients["mostly-sunny"], (0, 0))
        for cloud in self.clouds["mostly sunny"]:
            cloud.render(self.screen)
            if not self.DISABLEANIMATIONS:
                cloud.advance()
        self.screen.blit(self.lensFlare, (0, 0), special_flags=pygame.BLEND_RGB_ADD)



    def getImageWithOpacity(self, file, opacity, resize=True):
        image = pygame.image.load(file).convert()
        if resize == True:
            image = smartResize(image, self.RES)
        opacityLayer = pygame.surface.Surface(image.get_size(), pygame.SRCALPHA, 32).convert_alpha()
        opacityLayer.fill((0, 0, 0, 255-opacity))
        image.blit(opacityLayer, (0, 0))

        return image


    # Cloudy
    def cloudy(self):
        self.screen.fill(BLUEGREY)
        self.screen.blit(self.gradients["cloudy"], (0, 0))
        for cloud in self.clouds["cloudy"]:
            cloud.render(self.screen)
            if not self.DISABLEANIMATIONS:
                cloud.advance()
    

    # Rain
    def rain(self):
        self.screen.fill(BLUEGREY)
        self.screen.blit(self.gradients["rain"], (0, 0))
        if not self.DISABLEANIMATIONS:
            self.screen.blit(self.getMovingOverlay(), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        else:
            self.screen.blit(self.rainDrops, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    
    # Stormy
    def storm(self):
        self.screen.fill(BLUEGREY)
        
        if not self.DISABLEANIMATIONS:
            if self.flashing[0] and not self.DISABLELIGHTNING:
                self.screen.blit(self.gradients["lightning"], (0, 0))
            else:
                self.screen.blit(self.gradients["rain"], (0, 0))
        
        self.screen.blit(self.getMovingOverlay(), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        for cloud in self.clouds["cloudy"]:
            cloud.render(self.screen)
            if not self.DISABLEANIMATIONS:
                cloud.advance()

        
        if not self.DISABLELIGHTNING and not self.DISABLEANIMATIONS:
            if self.currentFlash != [] or self.flashing[0] == True:
                # Continue flash animation
                self.flashing[1] -= 1
                if self.flashing[1] <= 0:
                    if self.currentFlash == []:
                        # End flash animation
                        self.flashing = [False, 0]
                    else:
                        self.flashing[0] = not self.flashing[0]
                        self.flashing[1] = self.currentFlash[0]
                        self.currentFlash = self.currentFlash[1:]
            
            else:
                # Random chance for flash
                if random.randint(1, 30*15) == 69:
                    self.flash()
    
    
    # Lightning flash
    def flash(self):
        self.currentFlash = random.choice(self.flashes)
        self.flashing[0] = True
        self.flashing[1] = self.currentFlash[0]
        self.currentFlash = self.currentFlash[1:]

        
    # Fog
    def fog(self):
        self.screen.fill(BLUEGREY)
        self.screen.blit(self.gradients["fog"], (0, 0))

        # Moving fog overlay
        self.screen.blit(self.fogOverlay, (round(self.fogPos), 0), special_flags=pygame.BLEND_RGB_ADD)
        self.screen.blit(self.fogOverlay, (round(self.fogPos - self.fogOverlay.get_width()), 0), special_flags=pygame.BLEND_RGB_ADD)

        if not self.DISABLEANIMATIONS:
            self.fogPos += 0.5
            if self.fogPos > self.WIDTH:
                self.fogPos = 0


    def getMovingOverlay(self):
        """Gets the next frame in the moving overlay"""
        if not self.DISABLEANIMATIONS:
            self.movingIndex += 1
            if self.movingIndex >= len(self.movingOverlay):
                self.movingIndex = 0
        
        if self.movingOverlay[self.movingIndex].get_size() != self.RES:
            return pygame.transform.scale(self.movingOverlay[self.movingIndex], (round(self.overlayDimensions[0]), round(self.overlayDimensions[1])))
        
        return self.movingOverlay[self.movingIndex]
    

    def loadMovingOverlay(self, folder, opacity=255):
        """Loads a moving overlay like rain or snow"""
        if self.loadedOverlay != folder:
            self.movingOverlay = []
            self.opacityLayer = pygame.surface.Surface(self.RES, pygame.SRCALPHA, 32).convert_alpha()
            self.opacityLayer.fill((0, 0, 0, 255-opacity))

            for file in [f for f in os.listdir(folder) if os.path.isfile(join(folder, f))]:
                img = pygame.image.load(join(folder, file)).convert()
                img = smartResize(img, (self.RES[0]//2, self.RES[1]//2), True)
                img.blit(self.opacityLayer, (0, 0))
                self.movingOverlay.append(img)

                if self.DISABLEANIMATIONS:
                    # Only load the first frame to save memory
                    break
            
            # Compute the value the overlay needs to be rescaled to, to prevent calculating this each frame
            self.overlayDimensions = getSmartScale((self.RES[0]//2, self.RES[1]//2), self.RES)
            self.loadedOverlay = folder
            del self.opacityLayer
    

    def generateGradient(self, dimensions, color, startOP, endOP, duration):
        """Generates a surface with a colour gradually fading in/out vertically"""
        gradient = pygame.Surface(dimensions, pygame.SRCALPHA, 32)
        pArray = pygame.PixelArray(gradient)
        gradient = gradient.convert_alpha()

        interval = duration / ((startOP - endOP) + 1)
        for h in range(dimensions[1]):
            opacity = startOP - (h // interval)
            if opacity < endOP:
                opacity = endOP

            pArray[:, h] = (*color, opacity)
        
        return pArray.make_surface()