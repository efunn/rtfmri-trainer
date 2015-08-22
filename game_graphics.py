import pygame
from pygame.gfxdraw import aacircle

def draw_filled_aacircle(screen, radius, color, xpos, ypos):
    pygame.gfxdraw.filled_circle(screen,
                                 int(xpos),
                                 int(ypos),
                                 int(radius),
                                 color)
    pygame.gfxdraw.aacircle(screen,
                            int(xpos),
                            int(ypos),
                            int(radius),
                            color)

def draw_center_rect(screen, width, height, color, xpos, ypos):
    rect = pygame.Rect(xpos-0.5*width,
                       ypos-0.5*height,
                       width,
                       height)
    pygame.draw.rect(screen, color, rect)        

def make_text(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()

def draw_msg(screen, text, color=(255,255,255),
             center=(1024/2,768/2), size=50):
    font = pygame.font.Font('freesansbold.ttf', size)
    text_surf, text_rect = make_text(text, font, color)
    text_rect.center = center
    screen.blit(text_surf, text_rect)

