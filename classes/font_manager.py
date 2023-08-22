import pygame

WHITE = (255, 255, 255)

class FontManager:

    def __init__(self, resolution):
        """
        A class to keep track of all the different sizes of fonts used
        Font sizes are defined as fractions to ensure the display scales between all 16:9 resolutions
        """
        self.width, self.height = resolution

        fontDir = "fonts\\Martel_Sans\\MartelSans-"
        self.busNum = pygame.font.Font(fontDir+"SemiBold.ttf", round((128/720)*self.height))
        self.subtitle = pygame.font.Font(fontDir+"Regular.ttf", round((24/720)*self.height))
        self.stopName = pygame.font.Font(fontDir+"Regular.ttf", round((36/720)*self.height))
        self.nextTime = pygame.font.Font(fontDir+"SemiBold.ttf", round((62/720)*self.height))
        self.nextTimeSmaller = pygame.font.Font(fontDir+"SemiBold.ttf", round((55/720)*self.height))
        self.nextTimeList = pygame.font.Font(fontDir+"Regular.ttf", round((32/720)*self.height))
        self.temperature = pygame.font.Font(fontDir+"Regular.ttf", round((110/720)*self.height))
        self.weather = pygame.font.Font(fontDir+"Regular.ttf", round((52/720)*self.height))
        self.smallweatherdata = pygame.font.Font(fontDir+"Regular.ttf", round((20/720)*self.height))
        self.forecast = self.subtitle
        self.statusFont = pygame.font.Font(fontDir+"Regular.ttf", round((13/720)*self.height))
        self.timeFont = pygame.font.Font(fontDir+"Regular.ttf", round((41/720)*self.height))
    

    def renderAndBlit(self, text, font, surface, coords, color=WHITE, centre=True, anchor=(0, 0), mode=0):
        """Renders some text in the given font and blits it onto the given surface"""
        textSurface = font.render(text, True, color)

        if centre == True:
            coords = self.centreCoords(textSurface, coords, anchor)
        
        surface.blit(textSurface, coords, special_flags=mode)
    

    
    def centreAndBlitImage(self, image, surface, coords, centre=True):
        """An additional function to centre an image"""
        if centre == True:
            coords = self.centreCoords(image, coords)
        
        surface.blit(image, coords)


    def centreCoords(self, surface, coords, anchor=(0, 0)):
        """
        Shifts the coordinates to the midpoint of the surface
        Also shifts the coordinates based on the given anchor value
        """

        coords = list(coords)

        w, h = surface.get_size()

        coords[0] -= w//2 - anchor[0]*w
        coords[1] -= h//2 - anchor[1]*h
    
        return coords