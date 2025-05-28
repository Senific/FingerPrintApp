# test_sdl.py
import pygame
import os
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_VIDEODRIVER', 'fbcon')
pygame.init()
screen = pygame.display.set_mode((480, 320))
screen.fill((255, 0, 0))
pygame.display.update()
input("Press Enter to quit...")