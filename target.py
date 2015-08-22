from random import random
import numpy as np
import game_filter as gf
import game_graphics as gg

class Target(object):

    def __init__(self, screen, frame_rate, rad,
                 error_cutoff, min_error, ss_error,
                 min_success, start_coords,
                 target_lims, dof=1):
        self.ERROR_CUTOFF = error_cutoff
        self.MIN_ERROR_METRIC = min_error
        self.SS_ERROR_METRIC = ss_error
        self.MIN_SUCCESS_SCORE = min_success
        self.screen = screen
        self.screen_mid = 0.5*self.screen.get_width(), 0.5*self.screen.get_height()
        self.pos = np.array([-100,-100])
        self.dof = dof
        self.start_coords = start_coords
        self.target_lims = target_lims
        self.target_lims = [0,0]
        self.draw_bool = False
        self.color = (30,100,30)
        self.outline_color = (40,40,40)
        self.outline_rad = 2
        self.rad = rad

        self.hrf = gf.gen_hrf(frame_rate)
        self.impulse = np.zeros(len(self.hrf))
        self.impulse[-1] = 1
        self.set_fb_mode('impulse')

        self.error = 0
        self.error_metric = 0

        self.set_dof(dof)

        ########################
        # error metric buffers #
        ########################
        self.error_metric_buffer = np.zeros(len(self.hrf))
        self.error_metric_conv_buffer = np.zeros(len(self.hrf))
        self.error_metric_conv_sampled_buffer = np.zeros(len(self.hrf))


    def update(self, cursor_pos):
        self.error_metric_buffer = np.roll(self.error_metric_buffer, -1) 
        self.error_metric_conv_buffer = np.roll(self.error_metric_conv_buffer, -1) 
        if self.dof == 1:
            self.error = abs(self.pos[0]-cursor_pos[0])
        elif self.dof == 2:
            self.error = np.linalg.norm(self.pos-cursor_pos)
        self.error_metric_buffer[-1] = self.error_transform(self.error)
        self.error_metric_conv_buffer[-1] = np.dot(self.impulse_response,
                                                   self.error_metric_buffer)

    def draw(self):
        if self.draw_bool:
            if self.dof == 1:
                gg.draw_center_rect(self.screen, 2*(self.rad+self.outline_rad), 2*self.screen_mid[1],
                                    self.outline_color, self.pos[0], self.screen_mid[1])
                gg.draw_center_rect(self.screen, 2*self.rad, 2*self.screen_mid[1],
                                    self.color, self.pos[0], self.screen_mid[1])
            elif self.dof == 2:
                gg.draw_filled_aacircle(self.screen, self.rad+self.outline_rad, self.outline_color,
                                        self.pos[0], self.pos[1])
                gg.draw_filled_aacircle(self.screen, self.rad, self.color,
                                        self.pos[0], self.pos[1])

    def set_dof(self, dof):
        self.dof = dof

    def set_fb_mode(self, mode):
        if mode == 'impulse':
            self.fb_mode = 'impulse'
            self.impulse_response = self.impulse
        elif mode == 'hrf':
            self.fb_mode = 'hrf'
            self.impulse_response = self.hrf

    def set_new_target(self):
        self.get_random_pos()
        self.error_metric = self.MIN_ERROR_METRIC
        self.error_metric_buffer[:] = self.MIN_ERROR_METRIC
        self.error_metric_conv_buffer[:] = self.MIN_ERROR_METRIC
        self.error_metric_conv_sampled_buffer[:] = self.MIN_ERROR_METRIC

    def get_random_pos(self):
        distance = (self.target_lims[0]
                    + random()*(self.target_lims[1]-self.target_lims[0]))
        direction = random()

        if self.dof == 1:
            self.pos[1] = self.screen_mid[1]
            self.pos[0] = self.start_coords[0] + distance
        elif self.dof == 2:
            angle = direction*0.5*np.pi
            self.pos[0] = self.start_coords[0] + distance*np.cos(angle)
            self.pos[1] = self.start_coords[1] - distance*np.sin(angle)

    def error_transform(self, error):
        if error != self.ERROR_CUTOFF:
            error_metric = ((self.SS_ERROR_METRIC-self.MIN_ERROR_METRIC)
                            *(self.ERROR_CUTOFF-error)
                            /self.ERROR_CUTOFF+self.MIN_ERROR_METRIC)
        else:
            error_metric = 0
        if error_metric < self.MIN_ERROR_METRIC:
            error_metric = self.MIN_ERROR_METRIC
        return error_metric       
