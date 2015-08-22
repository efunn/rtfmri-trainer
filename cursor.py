import pygame
import numpy as np

import game_graphics as gg

class Cursor(object):
    def __init__(self, screen, dof=1):
        self.init_base_vars(screen, dof)
        self.init_custom_vars()
        self.init_game_logic()

    def init_base_vars(self, screen, dof):
        self.RAD = 5
        self.OUTLINE_THK = 2
        self.BASE_COLOR = 240,240,140
        self.OUTLINE_COLOR = 20,20,20
        self.pos = np.array([0,0])
        self.dof = dof
        self.screen = screen
        self.color = self.BASE_COLOR
        self.screen_mid = np.array([0.5*self.screen.get_width(),
                                    0.5*self.screen.get_height()])
        self.pos_lims = (self.screen_mid[0]-self.screen_mid[1]+self.RAD,
                         self.screen_mid[0]+self.screen_mid[1]-self.RAD,
                         self.RAD,
                         2*self.screen_mid[1]-self.RAD)

    def init_custom_vars(self):
        pass

    def init_game_logic(self):
        self.has_left = False
        self.start_ready = False
        self.in_start = False

    def set_dof(self, dof):
        self.dof = dof

    def update(self, new_pos): 
        self.pos[:] = new_pos[0], new_pos[1]
        self.trap()

    def trap(self):
        if self.pos[0] < self.pos_lims[0]:
            self.pos[0] = self.pos_lims[0]
        elif self.pos[0] > self.pos_lims[1]:
            self.pos[0] = self.pos_lims[1]
        if self.pos[1] < self.pos_lims[2]:
            self.pos[1] = self.pos_lims[2]
        elif self.pos[1] > self.pos_lims[3]:
            self.pos[1] = self.pos_lims[3]


    def draw(self): 
        if self.dof == 1:
            gg.draw_center_rect(self.screen, 2*(self.RAD+self.OUTLINE_THK), 2*self.screen_mid[1],
                                self.OUTLINE_COLOR, self.pos[0], self.screen_mid[1])
            gg.draw_center_rect(self.screen, 2*self.RAD, 2*self.screen_mid[1],
                                self.color, self.pos[0], self.screen_mid[1])
        elif self.dof == 2:
            gg.draw_filled_aacircle(self.screen, self.RAD+self.OUTLINE_THK, self.OUTLINE_COLOR,
                                    self.pos[0], self.pos[1])
            gg.draw_filled_aacircle(self.screen, self.RAD, self.color,
                                    self.pos[0], self.pos[1])

