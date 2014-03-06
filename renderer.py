import threading
import time

import pygame
from pygame.locals import *

import sgc

pygame.display.init()
pygame.font.init()

SIZE = 4

window = sgc.surface.Screen((1024,768),flags=pygame.DOUBLEBUF|pygame.RESIZABLE)

class Renderer(threading.Thread):
    def __init__(self, messages_from_engine):
        threading.Thread.__init__(self)
        self._messages_from_engine = messages_from_engine
        self.daemon = True

        self._world = None

    def run(self):
        cl = pygame.time.Clock()
        sx = 0
        sy = 0
        overlay = pygame.surface.Surface((150 * SIZE * 4, 150 *  SIZE * 4), pygame.SRCALPHA)
        background = pygame.surface.Surface((150 * SIZE * 4, 150 *  SIZE * 4), pygame.SRCALPHA)
        background.fill((255,255,255,0))
        for x in range(150):
            for y in range(150):
                self._draw_hexagon(background, x, y, SIZE, 0,0)
        while(True):
            time = cl.tick(10)

            for event in pygame.event.get():
                sgc.event(event)
                if event.type == QUIT:
                    running = not running
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        sy += 5
                    elif event.button == 5:
                        sy -= 5
                    elif event.button == 6:
                        sx += 5
                    elif event.button == 7:
                        sx -= 5
                if event.type == VIDEORESIZE:
                    global window
                    window = sgc.surface.Screen(event.size,flags=pygame.DOUBLEBUF|pygame.RESIZABLE)

                    window.fill((255,255,255))

                    window.blit(overlay, (sx,sy))

                    window.blit(background, (sx,sy))

            if len(self._messages_from_engine) > 0:
                message = self._messages_from_engine.pop(0)
                if message[0] == "draw_world":
                    self._world = message[1]    

                    overlay.fill((255,255,255,0))


                    for x in range(150):
                        for y in range(150):
                            if self._world:
                                if len(self._world[x][y]["markers"]):
                                    self._draw_markers(overlay, self._world[x][y]["markers"], x, y, SIZE, 0,0)
                                if self._world[x][y]["rock"]:
                                    self._draw_rock(overlay, x, y, SIZE, 0,0)
                                if self._world[x][y]["foods"]>0:
                                    self._draw_food(overlay, self._world[x][y]["foods"], x, y, SIZE, 0,0)
                                if self._world[x][y]["ant"]:
                                    self._draw_ant(overlay, self._world[x][y]["ant"], x, y, SIZE, 0,0)



            window.fill((255,255,255))

            window.blit(overlay, (sx,sy))

            window.blit(background, (sx,sy))
        
            
            #sgc.update(time)

            pygame.display.flip()

    def _draw_hexagon(self, window, x, y, size, sx, sy):
        if y % 2 == 0:
            x*=4
            y*=3
        else:
            x = x*4+2
            y*=3
        pygame.draw.line(window, (200,200,200), (x*size+sx,(y+1)*size+sy), ((x+2)*size+sx, y*size+sy))
        pygame.draw.line(window, (200,200,200), ((x+2)*size+sx, y*size+sy), ((x+4)*size+sx, (y+1)*size+sy))
        pygame.draw.line(window, (200,200,200), ((x+4)*size+sx, (y+1)*size+sy), ((x+4)*size+sx, (y+3)*size+sy))
        pygame.draw.line(window, (200,200,200), ((x+4)*size+sx, (y+3)*size+sy), ((x+2)*size+sx, (y+4)*size+sy))
        pygame.draw.line(window, (200,200,200), ((x+2)*size+sx, (y+4)*size+sy), ((x)*size+sx, (y+3)*size+sy))
        pygame.draw.line(window, (200,200,200), ((x)*size+sx, (y+3)*size+sy), (x*size+sx,(y+1)*size+sy))

    def _draw_rock(self, window, x, y, size, sx, sy):
        if y % 2 == 0:
            x*=4
            y*=3
        else:
            x = x*4+2
            y*=3
        pygame.draw.line(window, (0,0,0), (x*size+sx,(y+1)*size+sy), ((x+4)*size+sx, (y+3)*size+sy))
        pygame.draw.line(window, (0,0,0), ((x+2)*size+sx, y*size+sy), ((x+2)*size+sx, (y+4)*size+sy))
        pygame.draw.line(window, (0,0,0), ((x+4)*size+sx, (y+1)*size+sy), ((x)*size+sx, (y+3)*size+sy))

    def _draw_ant(self, window, ant, x, y, size, sx, sy):
        if y % 2 == 0:
            x*=4
            y*=3
        else:
            x = x*4+2
            y*=3
        if ant.color == "red":
            color = (255,0,0)
        elif ant.color == "black":
            color = (0, 0, 0)

        ant_surf = pygame.surface.Surface((4*SIZE,4*SIZE), flags=pygame.SRCALPHA)


        lines = ((4*size,2*size),
                 (0*size, 1*size),
                 (0*size, 3*size))

        width = 0 if ant._has_food else 1
        pygame.draw.polygon(ant_surf, color, lines, width)

        ant_surf = pygame.transform.rotate(ant_surf, -60 * ant._direction)

        padding = (ant_surf.get_rect()[2] - (size*4))/2


        window.blit(ant_surf, (x*size+sx - padding, y*size + sy - padding))


    def _draw_markers(self, window, markers, x, y, size, sx, sy):
        if y % 2 == 0:
            x*=4
            y*=3
        else:
            x = x*4+2
            y*=3
        color = (0,255,0)
        for m in markers:
            if m[1] == "red":
                color = (255,100,100)
            elif m[1] == "black":
                color = (100,100,100)
                
            if m[0] == 0:
                lines = (((x+2)*size+sx,(y+2)*size+sy),
                         ((x+2)*size+sx, y*size+sy),
                         ((x+4)*size+sx, (y+1)*size+sy))
            elif m[0] == 1:
                lines = (((x+2)*size+sx,(y+2)*size+sy),
                         ((x+4)*size+sx, (y+3)*size+sy),
                         ((x+4)*size+sx, (y+1)*size+sy))
            elif m[0] == 2:
                lines = (((x+2)*size+sx,(y+2)*size+sy),
                         ((x+4)*size+sx, (y+3)*size+sy),
                         ((x+2)*size+sx, (y+4)*size+sy))
            elif m[0] == 3:
                lines = (((x+2)*size+sx,(y+2)*size+sy),
                         ((x)*size+sx, (y+3)*size+sy),
                         ((x+2)*size+sx, (y+4)*size+sy))
            elif m[0] == 4:
                lines = (((x+2)*size+sx,(y+2)*size+sy),
                         ((x)*size+sx, (y+3)*size+sy),
                         ((x)*size+sx, (y+1)*size+sy))
            elif m[0] == 5:
                lines = (((x+2)*size+sx,(y+2)*size+sy),
                         ((x+2)*size+sx, y*size+sy),
                         ((x)*size+sx, (y+1)*size+sy))

            pygame.draw.polygon(window, color, lines, 0)


    def _draw_food(self, window, foods, x, y, size, sx, sy):
        if y % 2 == 0:
            x*=4
            y*=3
        else:
            x = x*4+2
            y*=3
        color = (0,0,255)
        pygame.draw.line(window, color, (x*size+sx,(y+1)*size+sy), ((x+4)*size+sx, (y+3)*size+sy))
        pygame.draw.line(window, color, ((x+2)*size+sx, y*size+sy), ((x+2)*size+sx, (y+4)*size+sy))
        pygame.draw.line(window, color, ((x+4)*size+sx, (y+1)*size+sy), ((x)*size+sx, (y+3)*size+sy))

