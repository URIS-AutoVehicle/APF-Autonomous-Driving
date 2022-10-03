
import pygame
from pygame.locals import *
import os
import sys
import math
import pygame
import pygame.mixer
from pygame.locals import *

THRESHOLD = 0.001

def echo():
    pygame.init()

    j1 = pygame.joystick.Joystick(1)
    j1.init()
    j2 = pygame.joystick.Joystick(0)
    j2.init()

    black = 0, 0, 0
    white = 255, 255, 255
    red = 255, 0, 0
    green = 0, 255, 0
    blue = 0, 0, 255

    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Physics")

    cur = (0,-1,-1)
    prev = (0,-1,-1)

    while True:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

            elif event.type == pygame.JOYBUTTONDOWN:
                print(f'device 1 b4@{j1.get_button(4)} b5@{j1.get_button(5)} trigger')

                if j1.get_button(0):
                    print(f'device 1 trigger')
                elif j2.get_button(0):
                    print(f'device 2 trigger')

            elif event.type == pygame.JOYAXISMOTION:
                cur = (j1.get_axis(0), j1.get_axis(1), j1.get_axis(2))
                axis_changed = (abs(cur[i] - prev[i] >= THRESHOLD) for i in range(3))
                if True in axis_changed:
                    print(f'axis 0@{j1.get_axis(0)} 1@{j1.get_axis(1)} 2@{j1.get_axis(2)} on device 1')
                prev = (j1.get_axis(0), j1.get_axis(1), j1.get_axis(2))
            elif event.type == pygame.JOYBALLMOTION:
                print(f'joy ball motion')
            elif event.type == pygame.JOYHATMOTION:
                print(f'joy hat motion')

        screen.fill(white)

        pygame.display.flip()


        '''
        elif event.type == pygame.JOYAXISMOTION:
            global j1, j2
            print(f'axis 0@{j1.get_axis(0)} 1@{j1.get_axis(1)} 2@{j1.get_axis(2)} on device 1\r', end='')
        '''

if __name__ == '__main__':
    echo()