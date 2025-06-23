"""
Clone of Doom, simple code that emulates the 1993 first-person shooter game Doom by id Software
"""

import pygame as pg
import sys
from settings import *

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()






