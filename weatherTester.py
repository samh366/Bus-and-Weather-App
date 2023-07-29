import os
import random
from datetime import datetime

import pygame

pygame.init()
pygame.font.init()

WIDTH = 1280
HEIGHT = 720
RES = (WIDTH, HEIGHT)
WHITE = (255, 255, 255)
GREY = (175, 175, 175)
BLUE = (72, 166, 207)
BLUEGREY = (77, 111, 125)
DARKBLUE = (0, 15, 48)

TIMEOUT = 10


# Resize an image maintaining aspect ratio
def smartResize(surface, newSize, smooth=False):
    """Resizes an image while keeping aspect ratio"""
    size = surface.get_size()
    x = abs(newSize[0] - size[0])
    y = abs(newSize[1] - size[1])

    if x <= y:
        scale = newSize[0]/size[0]
    else:
        scale = newSize[1]/size[1]
    finalSize = (size[0]*scale, size[1]*scale)

    if smooth == True:
        surface = pygame.transform.smoothscale(surface, (round(finalSize[0]), round(finalSize[1])))
    else:
        surface = pygame.transform.scale(surface, (round(finalSize[0]), round(finalSize[1])))
    
    return surface

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.running = True
        
        self.weather = WeatherManager(self.screen)

        self.weather.setWeather("snow")

        self.debugWeatherIndex = -1
        self.debugWeatherCodes = ["sunny", "partly-sunny",
                                  "cloudy", "rain",
                                  "snow", "clear", "mostly-clear"]



    def main(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    
                    if event.key == pygame.K_SPACE:
                        self.weather.setWeather(random.choice(["clear", "mostly-clear"]))
                    
                    if event.key == pygame.K_RIGHT:
                        self.debugWeatherIndex += 1

                        if self.debugWeatherIndex >= len(self.debugWeatherCodes):
                            self.debugWeatherIndex = 0
                        
                        self.weather.setWeather(self.debugWeatherCodes[self.debugWeatherIndex])
                    
                    if event.key == pygame.K_LEFT:
                        self.debugWeatherIndex -= 1

                        if self.debugWeatherIndex < 0:
                            self.debugWeatherIndex = len(self.debugWeatherCodes)-1
                        
                        self.weather.setWeather(self.debugWeatherCodes[self.debugWeatherIndex])

 
            self.weather.renderWeather()


            pygame.display.flip()
            self.clock.tick(30)



class Cloud:
    def __init__(self, image, opacity, size, pos):
        self.image = pygame.image.load(image)
        self.image = smartResize(self.image, size)
        self.image.set_alpha(opacity)
        self.size = self.image.get_size()

        self.pos = list(pos)

        self.randSpeed()
    

    def render(self, surface):
        surface.blit(self.image, self.roundPos())
    
    def randSpeed(self):
        self.speed = -1 * random.uniform(0.07, 0.2)
    
    def flip(self):
        self.image = pygame.transform.flip(self.image, flip_y=False, flip_x=True)

    
    def advance(self):
        self.pos = [self.pos[0]+self.speed, self.pos[1]]
        # Check if a loop is needed
        if self.pos[0] > WIDTH+110:
            self.pos[0] = -self.size[0]
            self.randSpeed()
        
        if self.pos[0] < -self.size[0]-10:
            self.pos[0] = WIDTH + 100
            self.randSpeed()
    

    def roundPos(self):
        return [round(self.pos[0]), round(self.pos[1])]



class WeatherManager:
    def __init__(self, screen):
        """Generates weather based on the given conditions"""
        self.screen = screen
        self.activeWeather = self.mostlySunny
        self.loading = False

        self.clouds = {
            "cloudy" : [
                Cloud("weather\\clouds\\big_cloud.png", 220, (500, 500), pos=(random.randint(800, 1000), random.randint(-30, 20))),
                Cloud("weather\\clouds\\big_cloud.png", 220, (500, 500), pos=(random.randint(-300, 400), random.randint(-30, 20)))
            ],
            "mostly sunny" : [
                Cloud("weather\\clouds\\cloud3.png", 220, (400, 400), pos=(random.randint(800, 1000), random.randint(-30, 20))),
                Cloud("weather\\clouds\\cloud4.png", 230, (300, 300), pos=(random.randint(-300, 400), random.randint(-30, 20)))
            ],
            "mostly clear" : [
                Cloud("weather\\clouds\\dark_cloud1.png", 180, size=(400, 400), pos=(random.randint(800, 1000), random.randint(-30, 20))),
                Cloud("weather\\clouds\\dark_cloud2.png", 180, size=(300, 300), pos=(random.randint(-300, 400), random.randint(-30, 20)))
            ]
        }

        self.clouds["cloudy"][1].flip()

        self.gradients = {
            "cloudy" : self.generateGradient(RES, (100, 100, 100), 230, 130, HEIGHT*1.2),
            "rain" : self.generateGradient(RES, (50, 50, 50), 255, 180, HEIGHT*1.3),
            "mostly-sunny" : self.generateGradient(RES, (255, 244, 191), 40, 0, HEIGHT*1.1),
            "clear" : self.generateGradient(RES, (0, 0, 0), 100, 0, HEIGHT*0.9),
            "stars" : self.generateGradient(RES, (0, 0, 0), 220, 0, HEIGHT*0.8),
            "snow" : self.generateGradient(RES, (100, 100, 100), 255, 180, HEIGHT*1.3)
        }

        self.lensFlare = self.getImageWithOpacity("weather\\sunny\\lens flare.png", opacity=150)
        self.stars = self.getImageWithOpacity("weather\\stars\\bigstars.png", opacity=150, resize=False)
        self.dimStars = self.getImageWithOpacity("weather\\stars\\bigstars.png", opacity=100, resize=False)
        self.stars2 = self.getImageWithOpacity("weather\\stars\\stars.png", opacity=150)
        # Apply gradient to stars
        self.starAngle = 0
        self.starPos = 0

        # Moving overlay
        self.movingOverlay = []
        self.movingIndex = 0


    def rotate(self, surface, angle, pivot, offset):
        """
        Rotates a surface around a point
        Pivot controls where the surface is rotated around on the screen.
        Offset determines what point on the surface is the centre to rotate around
        """
        rotated = pygame.transform.rotozoom(surface, -angle, 1)
        rotated_offset = offset.rotate(angle)

        # Realign image
        rect = rotated.get_rect(center=pivot+rotated_offset)
        return rotated, rect


    def setWeather(self, weathercode):
        """Sets the function to be used to display the weather and loads any needed overlays"""

        weathercode = weathercode.lower().replace(" ", "-")

        if weathercode == "cloudy":
            self.activeWeather = self.cloudy
        elif weathercode == "rain" or "showers" in weathercode:
            self.loadMovingOverlay("weather\\rain\\", 150)
            self.activeWeather = self.rain
        elif weathercode == "mostly-sunny":
            self.activeWeather = self.mostlySunny
        elif weathercode == "sunny":
            self.activeWeather = self.sunny
        elif weathercode == "clear":
            self.activeWeather = self.clear
        elif weathercode == "mostly-clear":
            self.activeWeather = self.mostlyClear
        elif weathercode == "snow":
            self.loadMovingOverlay("weather\\snow\\", 150)
            self.activeWeather = self.snow
        
        else:
            self.activeWeather = self.mostlySunny



    def renderWeather(self):
        """Renders the active weather state to the screen, to be called every frame"""
        self.activeWeather()

    
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
            cloud.advance()

    
    # Clear
    def clear(self):
        self.starAngle += 0.035
        self.screen.fill(DARKBLUE)
        self.screen.blit(self.gradients["clear"], (0, 0))

        starSurface = pygame.surface.Surface(RES)
        starSurface.blit(self.stars2, (0, self.starPos))
        starSurface.blit(self.stars2, (0, self.starPos-HEIGHT))

        self.starPos += 0.3
        if self.starPos > HEIGHT:
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
            cloud.advance()
        self.screen.blit(self.lensFlare, (0, 0), special_flags=pygame.BLEND_RGB_ADD)



    def getImageWithOpacity(self, file, opacity, resize=True):
        image = pygame.image.load(file).convert()
        if resize == True:
            image = smartResize(image, RES)
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
            cloud.advance()
    

    # Rain
    def rain(self):
        self.screen.fill(BLUEGREY)
        self.screen.blit(self.gradients["rain"], (0, 0))
        self.screen.blit(self.getMovingOverlay(), (0, 0), special_flags=pygame.BLEND_RGB_ADD)


    def getMovingOverlay(self):
        """Gets the next frame in the moving overlay"""
        self.movingIndex += 1
        if self.movingIndex >= len(self.movingOverlay):
            self.movingIndex = 0
        return self.movingOverlay[self.movingIndex]
    

    def loadMovingOverlay(self, folder, opacity=255):
        """Loads a moving overlay like rain or snow"""
        self.movingOverlay = []
        self.opacityLayer = pygame.surface.Surface(RES, pygame.SRCALPHA, 32).convert_alpha()
        self.opacityLayer.fill((0, 0, 0, 255-opacity))

        for file in [f for f in os.listdir(folder) if os.path.isfile(folder+f)]:
            img = pygame.image.load(folder+file).convert()
            img = smartResize(img, RES, True)
            img.blit(self.opacityLayer, (0, 0))
            self.movingOverlay.append(img)
        
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


if __name__ == "__main__":
    app = App()
    app.main()

    pygame.quit()
    quit()