import json

import pygame


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



def mins_to_mins_hours(mins):
    """Converts 77 mins to 1h 17 mins as an example"""
    if mins == "Due now":
        return mins
    if ":" in mins:
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
    


def loadConfig(file):
    """Loads config info from config.txt"""
    with open(file, "r") as configfile:
        data = json.loads(configfile.read())
    
    return data