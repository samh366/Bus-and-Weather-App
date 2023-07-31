import random

import pygame

from classes.utils import smartResize


class Cloud:

    width = 1920

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
        if self.pos[0] > Cloud.width+110:
            self.pos[0] = -self.size[0]
            self.randSpeed()
        
        if self.pos[0] < -self.size[0]-10:
            self.pos[0] = Cloud.width + 100
            self.randSpeed()
    

    def roundPos(self):
        return [round(self.pos[0]), round(self.pos[1])]