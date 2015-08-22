import pygame
import numpy as np

class Thermometer(object):

    def __init__(self, screen,
                 min_height = 0.05,
                 target_height = 0.8,
                 max_height = 0.9):
        self.screen = screen
        self.score_color = (30,150,30)
        self.MIN_LINE_COLOR = (220,120,120)
        self.TARGET_LINE_COLOR = (220,220,80)
        self.MAX_LINE_COLOR = (120,220,120)
        self.MIN_LINE_COLOR_ALT = (80,30,30)
        self.TARGET_LINE_COLOR_ALT = (60,60,30)
        self.MAX_LINE_COLOR_ALT = (30,80,30)
        self.BORDER_RECTS_COLOR = (20,20,20)
        self.BG_COLOR = (40,40,40)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.therm_width = int(0.5*(self.screen_width-self.screen_height))
        self.score_tick_height = 4
        self.score_min_height = (1-min_height)*self.screen_height
        self.score_target_height = (1-target_height)*self.screen_height
        self.score_max_height = (1-max_height)*self.screen_height
        self.set_all_rects()

    def set_all_rects(self):

        self.rect_left = pygame.Rect(0,0,self.therm_width,0)
        self.set_rect_bottom_left(self.rect_left, 0)

        self.rect_right = pygame.Rect(0,0,self.therm_width,0)
        self.set_rect_bottom_right(self.rect_right, 0)

        self.bg_rect_left = pygame.Rect(0,0,self.therm_width,0)
        self.set_rect_bottom_left(self.bg_rect_left, self.screen_height)

        self.bg_rect_right = pygame.Rect(0,0,self.therm_width,0)
        self.set_rect_bottom_right(self.bg_rect_right, self.screen_height)

        self.rect_left_min_score = pygame.Rect(0,
                                               (self.score_min_height
                                                -0.5*self.score_tick_height),
                                               self.therm_width,
                                               self.score_tick_height)
        self.rect_right_min_score = pygame.Rect(self.rect_left_min_score)
        self.rect_right_min_score.right = self.screen_width

        self.rect_left_target_score = pygame.Rect(0,
                                               (self.score_target_height
                                                -0.5*self.score_tick_height),
                                               self.therm_width,
                                               self.score_tick_height)
        self.rect_right_target_score = pygame.Rect(self.rect_left_target_score)
        self.rect_right_target_score.right = self.screen_width

        self.rect_left_max_score = pygame.Rect(0,
                                               (self.score_max_height
                                                -0.5*self.score_tick_height),
                                               self.therm_width,
                                               self.score_tick_height)
        self.rect_right_max_score = pygame.Rect(self.rect_left_max_score)
        self.rect_right_max_score.right = self.screen_width

        self.border_rects = []
        self.border_rects.append(self.rect_left_min_score.inflate(0,2))
        self.border_rects.append(self.rect_left_target_score.inflate(0,2))
        self.border_rects.append(self.rect_left_max_score.inflate(0,2))
        self.border_rects.append(self.rect_right_min_score.inflate(0,2))
        self.border_rects.append(self.rect_right_target_score.inflate(0,2))
        self.border_rects.append(self.rect_right_max_score.inflate(0,2))

    def set_rect_bottom_left(self, rect, height):
        rect.height = height
        rect.bottom = self.screen_height
        rect.left = 0

    def set_rect_bottom_right(self, rect, height):
        rect.height = height
        rect.bottom = self.screen_height
        rect.right = self.screen_width

    def draw(self, active, score_1, score_2 = None):
        pygame.draw.rect(self.screen, self.BG_COLOR, self.bg_rect_left)
        pygame.draw.rect(self.screen, self.BG_COLOR, self.bg_rect_right)
        if active:
            if score_2 == None:
                score_2 = score_1

            self.set_rect_bottom_left(self.rect_left, score_1*self.screen_height)
            self.set_rect_bottom_right(self.rect_right, score_2*self.screen_height)

            pygame.draw.rect(self.screen, self.score_color, self.rect_left)
            pygame.draw.rect(self.screen, self.score_color, self.rect_right)

            for rect in self.border_rects:
                pygame.draw.rect(self.screen, self.BORDER_RECTS_COLOR, rect)
            pygame.draw.rect(self.screen, self.MIN_LINE_COLOR, self.rect_left_min_score)
            pygame.draw.rect(self.screen, self.MIN_LINE_COLOR, self.rect_right_min_score)
            pygame.draw.rect(self.screen, self.TARGET_LINE_COLOR, self.rect_left_target_score)
            pygame.draw.rect(self.screen, self.TARGET_LINE_COLOR, self.rect_right_target_score)
            pygame.draw.rect(self.screen, self.MAX_LINE_COLOR, self.rect_left_max_score)
            pygame.draw.rect(self.screen, self.MAX_LINE_COLOR, self.rect_right_max_score)
        else:
            for rect in self.border_rects:
                pygame.draw.rect(self.screen, self.BORDER_RECTS_COLOR, rect)
            pygame.draw.rect(self.screen, self.MIN_LINE_COLOR_ALT, self.rect_left_min_score)
            pygame.draw.rect(self.screen, self.MIN_LINE_COLOR_ALT, self.rect_right_min_score)
            pygame.draw.rect(self.screen, self.TARGET_LINE_COLOR_ALT, self.rect_left_target_score)
            pygame.draw.rect(self.screen, self.TARGET_LINE_COLOR_ALT, self.rect_right_target_score)
            pygame.draw.rect(self.screen, self.MAX_LINE_COLOR_ALT, self.rect_left_max_score)
            pygame.draw.rect(self.screen, self.MAX_LINE_COLOR_ALT, self.rect_right_max_score)



