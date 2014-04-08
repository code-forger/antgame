import threading
import time
import json

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
        self._selected = "-1"
        self._profile = [0 for x in range(100)]

        with open("titan.theme", "r") as f:
            self._colours = json.loads(f.read())

    def run(self):
        self._dragging = False
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
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._dragging = True
                        self._mouse = event.pos
                    elif event.button == 4:
                        global SIZE
                        oldsize = SIZE
                        SIZE += 1
                        if SIZE > 10:
                            SIZE = 10
                        if oldsize != SIZE:
                            overlay = pygame.surface.Surface((150 * SIZE * 4, 150 *  SIZE * 4), pygame.SRCALPHA)
                            background = pygame.surface.Surface((150 * SIZE * 4, 150 *  SIZE * 4), pygame.SRCALPHA)
                            background.fill((255,255,255,0))
                            for x in range(150):
                                for y in range(150):
                                    self._draw_hexagon(background, x, y, SIZE, 0,0)

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

                    elif event.button == 5:
                        global SIZE
                        oldsize = SIZE
                        SIZE -= 1
                        if SIZE < 1:
                            SIZE = 1
                        if oldsize != SIZE:

                            overlay = pygame.surface.Surface((150 * SIZE * 4, 150 *  SIZE * 4), pygame.SRCALPHA)
                            background = pygame.surface.Surface((150 * SIZE * 4, 150 *  SIZE * 4), pygame.SRCALPHA)
                            background.fill((255,255,255,0))
                            for x in range(150):
                                for y in range(150):
                                    self._draw_hexagon(background, x, y, SIZE, 0,0)
                            
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

                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self._dragging = False
                elif event.type == MOUSEMOTION:
                    if self._dragging:
                            sx -= self._mouse[0] - event.pos[0]
                            sy -= self._mouse[1] - event.pos[1]
                            self._mouse = event.pos
                if event.type == VIDEORESIZE:
                    global window
                    window = sgc.surface.Screen(event.size,flags=pygame.DOUBLEBUF|pygame.RESIZABLE)

                    window.fill(self._colours["background"])

                    window.blit(overlay, (sx,sy))

                    window.blit(background, (sx,sy))

            if len(self._messages_from_engine) > 0:
                message = self._messages_from_engine.pop(-1)
                self._messages_from_engine[:] = []
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
                if message[0] == "select_world":
                    print message[1], self._selected
                    self._selected = message[1]




            window.fill(self._colours["background"])

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
        pygame.draw.line(window, self._colours["cell_border"], (x*size+sx,(y+1)*size+sy), ((x+2)*size+sx, y*size+sy))
        pygame.draw.line(window, self._colours["cell_border"], ((x+2)*size+sx, y*size+sy), ((x+4)*size+sx, (y+1)*size+sy))
        pygame.draw.line(window, self._colours["cell_border"], ((x+4)*size+sx, (y+1)*size+sy), ((x+4)*size+sx, (y+3)*size+sy))
        pygame.draw.line(window, self._colours["cell_border"], ((x+4)*size+sx, (y+3)*size+sy), ((x+2)*size+sx, (y+4)*size+sy))
        pygame.draw.line(window, self._colours["cell_border"], ((x+2)*size+sx, (y+4)*size+sy), ((x)*size+sx, (y+3)*size+sy))
        pygame.draw.line(window, self._colours["cell_border"], ((x)*size+sx, (y+3)*size+sy), (x*size+sx,(y+1)*size+sy))

    def _draw_rock(self, window, x, y, size, sx, sy):
        if y % 2 == 0:
            x*=4
            y*=3
        else:
            x = x*4+2
            y*=3
        pygame.draw.line(window, self._colours["rocks"], (x*size+sx,(y+1)*size+sy), ((x+4)*size+sx, (y+3)*size+sy))
        pygame.draw.line(window, self._colours["rocks"], ((x+2)*size+sx, y*size+sy), ((x+2)*size+sx, (y+4)*size+sy))
        pygame.draw.line(window, self._colours["rocks"], ((x+4)*size+sx, (y+1)*size+sy), ((x)*size+sx, (y+3)*size+sy))

    def _draw_ant(self, window, ant, x, y, size, sx, sy):
        try:
            if y % 2 == 0:
                x*=4
                y*=3
            else:
                x = x*4+2
                y*=3
            if ant.color == "red":
                color = self._colours["red_ant"]
            elif ant.color == "black":
                color = self._colours["black_ant"]

            ant_surf = pygame.surface.Surface((4*SIZE,4*SIZE), flags=pygame.SRCALPHA)


            lines = ((4*size,2*size),
                     (0*size, 1*size),
                     (0*size, 3*size))

            width = 0 if ant._has_food else 1
            pygame.draw.polygon(ant_surf, color, lines, width)

            ant_surf = pygame.transform.rotate(ant_surf, -60 * ant._direction)

            padding = (ant_surf.get_rect()[2] - (size*4))/2


            window.blit(ant_surf, (x*size+sx - padding, y*size + sy - padding))
        except Exception as e:
            pass


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
                color = self._colours["red_marker"]
            elif m[1] == "black":
                color = self._colours["black_marker"]
                
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
        color = self._colours["food"]

        lines = []
        for i in range(foods):
            if i == 0:
                lines.extend((((x+2)*size+sx,(y+2)*size+sy),
                                         ((x+2)*size+sx, y*size+sy),
                                         ((x+4)*size+sx, (y+1)*size+sy)))
            elif i == 1:
                lines.extend((((x+2)*size+sx,(y+2)*size+sy),
                                         ((x+4)*size+sx, (y+3)*size+sy),
                                         ((x+4)*size+sx, (y+1)*size+sy)))
            elif i == 2:
                lines.extend((((x+2)*size+sx,(y+2)*size+sy),
                                         ((x+4)*size+sx, (y+3)*size+sy),
                                         ((x+2)*size+sx, (y+4)*size+sy)))
            elif i == 3:
                lines.extend((((x+2)*size+sx,(y+2)*size+sy),
                                         ((x)*size+sx, (y+3)*size+sy),
                                         ((x+2)*size+sx, (y+4)*size+sy)))
            elif i == 4:
                lines.extend((((x+2)*size+sx,(y+2)*size+sy),
                                         ((x)*size+sx, (y+3)*size+sy),
                                         ((x)*size+sx, (y+1)*size+sy)))
            elif i == 5:
                lines.extend((((x+2)*size+sx,(y+2)*size+sy),
                                         ((x+2)*size+sx, y*size+sy),
                                         ((x)*size+sx, (y+1)*size+sy)))
        pygame.draw.polygon(window, color, lines, 0)

