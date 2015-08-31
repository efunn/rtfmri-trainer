import pygame
import sys
import yaml
import numpy as np

import game_graphics as gg
import game_run as gr
import fileutils as fu
from cursor import Cursor
from target import Target
from timer import Timer
from thermometer import Thermometer
try: 
    from pydaq import Pydaq
    SENSOR_ACTIVE = True
except:
    SENSOR_ACTIVE = False


class Trainer(object):

    def __init__(self):

        ###############
        # load config #
        ###############
        with open('trainer_config.yaml') as f:
            CONFIG = yaml.load(f)
        self.exp_type = CONFIG['experiment-type']
        self.playback_bool = CONFIG['playback-enabled']
        self.subj_id = CONFIG['subject-id']
        self.subj_dir = 'datasets/' + self.subj_id
        if self.exp_type == 'timed':
            fu.write_all_headers_timed(self)
        elif self.exp_type == 'block':
            fu.write_all_headers_block(self)

        #################
        # set constants #
        #################
        self.FRAME_RATE = 30
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1024, 768
        self.BG_COLOR_REG = 70,70,70
        self.BG_COLOR_REG_2 = 110,110,110
        self.BG_COLOR_REG_3 = 40,40,40
        self.SUCCESS_COLOR = 70,170,70
        self.INDICATOR_COLOR = 40,60,40
        self.INDICATOR_COLOR_2 = 30,100,30
        self.GOOD_MSG_COLOR = 160,255,160
        self.BAD_MSG_COLOR = 255,160,160
        self.A_MSG_COLOR = 160,160,255
        self.B_MSG_COLOR = 230,230,160
        self.SENSOR_INPUT_OFFSET = np.array([0.5*self.SCREEN_WIDTH,
                                             0.5*self.SCREEN_HEIGHT])
        self.NEWTONS_2_PIXEL = 200
        self.BLOCK_TIME = CONFIG['block-length']
        self.RESET_HOLD_TIME = 0.5
        self.REACH_SUCCESS_TIME = 2.
        self.NOISE_VAR_GOOD = 0.025
        if not self.playback_bool:
            self.NOISE_VAR_BAD = 10*self.NOISE_VAR_GOOD
        else:
            self.NOISE_VAR_BAD = self.NOISE_VAR_GOOD
        self.SAMPLE_PERIOD = 2.
        self.SAMPLE_FRAMES = self.SAMPLE_PERIOD*self.FRAME_RATE
        self.TRS_SHOW_UPDATE_RATE = 2
        self.TR_LIST = (0.125, .25, 0.5, 1., 2., 4.)
        self.TRS_SAMPLES_DICT = dict((tr, tr/self.SAMPLE_PERIOD)
                                     for tr in self.TR_LIST)
        self.TRS_SUCCESS_DICT = dict((tr, self.REACH_SUCCESS_TIME/tr)
                                     for tr in self.TR_LIST)
        self.BUFFER_DIST = 0.075*self.SCREEN_HEIGHT
        self.START_DIST = self.BUFFER_DIST
        self.GAME_ORIGIN = (0.5*self.SCREEN_WIDTH-0.5*self.SCREEN_HEIGHT,
                            self.SCREEN_HEIGHT)
        self.START_COORDS = np.array([self.GAME_ORIGIN[0]+self.BUFFER_DIST,
                                      self.GAME_ORIGIN[1]-self.BUFFER_DIST])
        self.TARGET_DIST = (0.3*self.SCREEN_HEIGHT,
                            0.8*self.SCREEN_HEIGHT)
        self.ERROR_CUTOFF = self.TARGET_DIST[0] - self.START_DIST
        self.MIN_ERROR_METRIC = 0.1
        self.SS_ERROR_METRIC = 0.9
        self.MIN_SUCCESS_SCORE = 0.7
        self.TARGET_RAD = (self.ERROR_CUTOFF*
                           (1-(self.MIN_SUCCESS_SCORE-self.MIN_ERROR_METRIC)
                            /(self.SS_ERROR_METRIC-self.MIN_ERROR_METRIC)))
        if SENSOR_ACTIVE:
            self.daq = Pydaq('Dev1/ai0:1', self.FRAME_RATE)
        self.VISIBLE_TRIALS = CONFIG['visible-trials']
        self.INVISIBLE_TRIALS = CONFIG['invisible-trials']
        self.NUM_TRIALS = self.VISIBLE_TRIALS
        self.TRIAL_TYPES = 8

        ####################################################
        # start pygame and initialize default game objects #
        ####################################################
        pygame.init()
        pygame.mouse.set_visible(not pygame.mouse.set_visible)
        self.clock = pygame.time.Clock()
        if CONFIG['fullscreen']:
            self.screen = pygame.display.set_mode(
                            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
                             pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        ##################################
        # initialize custom game objects #
        ##################################
        self.cursor = Cursor(self.screen)


        self.target = Target(self.screen,
                             self.FRAME_RATE,
                             self.TARGET_RAD,
                             self.ERROR_CUTOFF,
                             self.MIN_ERROR_METRIC,
                             self.SS_ERROR_METRIC,
                             self.MIN_SUCCESS_SCORE,
                             self.START_COORDS,
                             self.TARGET_DIST)

        self.therm = Thermometer(self.screen,
                                 self.MIN_ERROR_METRIC,
                                 self.MIN_SUCCESS_SCORE,
                                 self.SS_ERROR_METRIC)

        self.INDIC_RAD_MAX = self.START_DIST-self.cursor.RAD-2
        self.target.target_lims = self.TARGET_DIST
        self.timers = {}
        self.init_timers()
        self.set_tr(2.)
        self.trial_count = 0
        self.trial_type_count = 1
        self.next_dof = 1
        self.set_dof(self.next_dof)
        self.next_ir = 'impulse'
        self.next_visible = True
        self.set_trial()

        ######################
        # set game variables #
        ######################
        self.screen_mid = np.array([0.5*self.screen.get_width(),
                                    0.5*self.screen.get_height()])
        self.bg_color = self.BG_COLOR_REG
        self.bg_color_alt = self.BG_COLOR_REG_2
        self.bg_color_alt_2 = self.BG_COLOR_REG_3
        self.indicator_color = self.INDICATOR_COLOR
        self.indicator_rad = 0*self.START_DIST
        self.success_color = self.SUCCESS_COLOR
        self.input_mode = 'mouse'
        self.input_pos = np.array([0.0,0.0])
        self.training_mode = True

        #######################
        # set block variables #
        #######################
        self.NUM_BLOCK_TRIALS = CONFIG['num-block-trials'] 
        self.next_target = 'new'
        self.first_feedback = CONFIG['first-trial-feedback'] 
        self.first_noise = CONFIG['first-trial-noise']
        self.next_feedback = self.first_feedback
        self.next_noise = self.first_noise
        self.set_noise()
        self.BLOCK_TRS = self.BLOCK_TIME/self.tr
        self.block_nfb_buffer = np.zeros(self.BLOCK_TRS)
        self.block_tr_count = 0
        self.total_block_count = 0
        self.trial_block_count = 0

        ##########################
        # set playback variables #
        ##########################
        self.TIME_SHIFT = 6
        self.PLAYBACK_TRS = self.BLOCK_TRS + self.TIME_SHIFT/self.tr
        self.EXTRA_TRS = 2
        self.playback_buffer_length = (self.BLOCK_TIME
                                       + self.EXTRA_TRS)*self.FRAME_RATE
        self.move_counter = 0
        self.reset_playback_buffers()

    def reset_playback_buffers(self):
        self.playback_counter = 0
        self.playback_time_buffer = np.zeros(self.playback_buffer_length)
        self.playback_pos_buffer = np.zeros((2,self.playback_buffer_length))
        self.playback_nfb_buffer = np.zeros(self.playback_buffer_length)
        self.playback_nfb_points = np.zeros(self.PLAYBACK_TRS)


    def get_pos(self):
        if self.input_mode=='mouse' or not(SENSOR_ACTIVE):
            return pygame.mouse.get_pos()
        else:
            f_out = self.daq.get_force()
            return (self.SENSOR_INPUT_OFFSET[0]+self.NEWTONS_2_PIXEL*f_out[0], 
                    self.SENSOR_INPUT_OFFSET[1]+self.NEWTONS_2_PIXEL*f_out[1])


    def set_trial(self):
        self.set_dof(self.next_dof)
        self.target.set_fb_mode(self.next_ir)
        self.set_training_mode(self.next_visible)


    def set_noise(self):
        if self.next_noise == 'good':
            self.noise_var = self.NOISE_VAR_GOOD
        elif self.next_noise == 'bad':
            self.noise_var = self.NOISE_VAR_BAD


    def set_training_mode(self, bool_arg):
        self.training_mode = bool_arg


    def set_tr(self, tr):
        if tr == 0.125:
            self.tr = 0.125
            self.timers['tr'] = self.timers['tr_8hz']
        elif tr == 0.25:
            self.tr = 0.25
            self.timers['tr'] = self.timers['tr_4hz']
        elif tr == 0.5:
            self.tr = 0.5
            self.timers['tr'] = self.timers['tr_2hz']
        elif tr == 1:
            self.tr = 1.
            self.timers['tr'] = self.timers['tr_1hz']
        elif tr == 2:
            self.tr = 2.
            self.timers['tr'] = self.timers['tr_p5hz']
        elif tr == 4:
            self.tr = 4.
            self.timers['tr'] = self.timers['tr_p25hz']


    def init_timers(self):
        self.timers['signal'] = Timer(self.SAMPLE_PERIOD)
        self.timers['tr_8hz'] = Timer(self.TR_LIST[0])
        self.timers['tr_4hz'] = Timer(self.TR_LIST[1])
        self.timers['tr_2hz'] = Timer(self.TR_LIST[2])
        self.timers['tr_1hz'] = Timer(self.TR_LIST[3])
        self.timers['tr_p5hz'] = Timer(self.TR_LIST[4])
        self.timers['tr_p25hz'] = Timer(self.TR_LIST[5])
        self.timers['tr'] = self.timers['tr_2hz']
        self.timers['reach'] = Timer(0)
        self.timers['reach_hold'] = Timer(self.REACH_SUCCESS_TIME)
        self.timers['block'] = Timer(self.BLOCK_TIME)
        self.timers['reset_hold'] = Timer(self.RESET_HOLD_TIME)


    def reset_all_timers(self):
        for k,t in self.timers.iteritems():
            t.reset()


    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                elif event.key == pygame.K_0:
                    self.daq.set_volts_zero()
                elif event.key == pygame.K_f:
                    if self.dof == 1:
                        self.set_dof(2)
                    elif self.dof == 2:
                        self.set_dof(1)
                elif event.key == pygame.K_b:
                    self.target.set_new_target()
                elif event.key == pygame.K_v:
                    self.training_mode = not(self.training_mode)
                elif event.key == pygame.K_c:
                    self.target.set_fb_mode('hrf')
                elif event.key == pygame.K_x:
                    self.target.set_fb_mode('impulse')
                elif event.key == pygame.K_m:
                    if self.input_mode == 'mouse':
                        self.input_mode = 'sensor'
                    elif self.input_mode == 'sensor':
                        self.input_mode = 'mouse'

    def run_timed(self):
        ###########################################
        # main loop for time-to-target experiment #
        ###########################################
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.input_pos = self.get_pos()
            self.cursor.update(self.input_pos)
            self.target.update(self.cursor.pos)


            if not(self.timers['reset_hold'].time_limit_hit):
                gr.check_in_start(self, time_passed)
                self.target.draw_bool = True
            elif not(self.cursor.has_left):
                gr.check_if_left(self)
                self.target.draw_bool = False
            elif self.training_mode:
                self.target.draw_bool = True
            else:
                self.target.draw_bool = False

            if self.cursor.has_left:
                gr.frame_based_updates_timed(self)
                self.timers['signal'].update(time_passed)
                self.timers['tr'].update(time_passed)
                if self.timers['signal'].time_limit_hit:
                    gr.signal_based_updates(self)
                    if self.timers['tr'].time_limit_hit:
                        gr.tr_based_updates(self)

            self.draw_background()
            self.therm.draw(self.cursor.has_left,
                            self.target.error_metric)
            self.target.draw()
            if (self.trial_count == 0
                    and not self.cursor.has_left):
                self.draw_instructions_timed()
            self.cursor.draw()
            pygame.display.flip()

    def run_block(self):
        ###########################################
        # main loop for block feedback experiment #
        ###########################################
        self.target.draw_bool = False 
        if self.playback_bool:
            self.set_dof(1)
        else:
            self.set_dof(1)
        self.target.set_fb_mode('hrf')

        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.input_pos = self.get_pos()
            self.cursor.update(self.input_pos)
            self.target.update(self.cursor.pos)


            if not(self.timers['reset_hold'].time_limit_hit):
                gr.check_in_start(self, time_passed)
                if self.next_target == 'new':
                    self.target.draw_bool = True
            elif not(self.cursor.has_left):
                gr.check_if_left(self)
                self.target.draw_bool = False
            # debugging
            # self.target.draw_bool = True

            if self.cursor.has_left:
                gr.frame_based_updates_block(self)
                self.timers['signal'].update(time_passed)
                self.timers['tr'].update(time_passed)
                self.timers['block'].update(time_passed)
                if self.timers['signal'].time_limit_hit:
                    gr.signal_based_updates(self)
                    if self.timers['tr'].time_limit_hit:
                        gr.tr_based_updates(self)
                        if self.timers['block'].time_limit_hit:
                            gr.block_based_updates(self)

            self.draw_background()
            therm_draw_bool = ((self.cursor.has_left and
                                self.next_feedback == 'continuous')
                               or (self.total_block_count > 0 
                                   and not self.cursor.has_left))
            score = self.target.error_metric
            self.therm.draw(therm_draw_bool,
                            score)
            self.target.draw()
            if not self.cursor.has_left:
                self.draw_instructions_block()
            else:
                self.therm.set_score_color('norm')
            self.cursor.draw()
            pygame.display.flip()

    def run_playback(self):
        while self.move_counter > 0:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.cursor.update(self.playback_pos_buffer[:,
                                                        self.playback_counter])
            self.indicator_rad = int(self.INDIC_RAD_MAX*(
                                     self.playback_time_buffer[self.playback_counter]
                                     /float(self.timers['block'].MAX_TIME)))
            self.draw_background()
            self.therm.draw(True,
                            self.playback_nfb_buffer[self.playback_counter])
            # debugging
            # self.target.draw()
            self.cursor.draw()
            pygame.display.flip()
            self.move_counter -= 1
            self.playback_counter += 1

    def set_dof(self, dof):
        self.dof = dof
        self.cursor.set_dof(dof)
        self.target.set_dof(dof)

    def draw_background(self):
        self.screen.fill(self.bg_color_alt_2)
        gr.cap_indicator_rad(self)
        self.draw_play_area()
        if self.indicator_rad > 0:
            self.draw_indicator()

    def draw_instructions_block(self):
        if self.next_target == 'new':
            top_msg = 'New target'
            top_color = self.GOOD_MSG_COLOR
        else:
            top_msg = 'Same target'
            top_color = self.BAD_MSG_COLOR

        if self.next_feedback == 'continuous':
            mid_msg = 'Continuous feedback'
            mid_color = self.A_MSG_COLOR
        else:
            mid_msg = 'Intermittent feedback'
            mid_color = self.B_MSG_COLOR

        if self.next_noise == 'good':
            btm_msg = 'Good signal'
            btm_color = self.A_MSG_COLOR
        else:
            btm_msg = 'Bad signal'
            btm_color = self.B_MSG_COLOR

        gg.draw_msg(self.screen, top_msg,
                    color=top_color,
                    center=(self.screen_mid[0],
                            self.screen_mid[1]-75))
        gg.draw_msg(self.screen, mid_msg,
                    color=mid_color,
                    center=(self.screen_mid[0],
                            self.screen_mid[1]))
        if not self.playback_bool:
            gg.draw_msg(self.screen, btm_msg,
                        color=btm_color,
                        center=(self.screen_mid[0],
                                self.screen_mid[1]+75))

    def draw_instructions_timed(self):
        if self.next_visible:
            top_msg = 'Target visible'
            top_color = self.GOOD_MSG_COLOR
        else:
            top_msg = 'Target invisible'
            top_color = self.BAD_MSG_COLOR
        if self.next_ir == 'impulse':
            btm_msg = 'Instant feedback'
            btm_color = self.GOOD_MSG_COLOR
        else:
            btm_msg = 'Delayed feedback'
            btm_color = self.BAD_MSG_COLOR
        gg.draw_msg(self.screen, top_msg,
                    color=top_color,
                    center=(self.screen_mid[0],
                            self.screen_mid[1]-50))
        gg.draw_msg(self.screen, btm_msg,
                    color=btm_color,
                    center=(self.screen_mid[0],
                            self.screen_mid[1]+50))

    def draw_play_area(self):
        if self.dof == 1:
            gg.draw_center_rect(self.screen,
                                self.SCREEN_HEIGHT, self.SCREEN_HEIGHT,
                                self.bg_color,
                                self.screen_mid[0], self.screen_mid[1])

            gg.draw_center_rect(self.screen, 
                                self.TARGET_DIST[1]-self.TARGET_DIST[0],
                                self.SCREEN_HEIGHT,
                                self.bg_color_alt,
                                (self.TARGET_DIST[0]
                                 +0.5*(self.TARGET_DIST[1]
                                       -self.TARGET_DIST[0])
                                 + self.START_COORDS[0]),
                                self.screen_mid[1])

            gg.draw_center_rect(self.screen,
                                2*(self.START_DIST-self.cursor.RAD),
                                self.SCREEN_HEIGHT,
                                self.bg_color_alt_2,
                                self.START_COORDS[0],  self.screen_mid[1])

        elif self.dof == 2:
            gg.draw_center_rect(self.screen,
                                self.SCREEN_HEIGHT, self.SCREEN_HEIGHT,
                                self.bg_color,
                                self.screen_mid[0], self.screen_mid[1])

            gg.draw_filled_aacircle(self.screen,
                                    self.TARGET_DIST[1],
                                    self.bg_color_alt,
                                    self.START_COORDS[0], self.START_COORDS[1])

            gg.draw_filled_aacircle(self.screen,
                                    self.TARGET_DIST[0],
                                    self.bg_color,
                                    self.START_COORDS[0], self.START_COORDS[1])

            gg.draw_center_rect(self.screen,
                                self.SCREEN_HEIGHT, 2*self.BUFFER_DIST,
                                self.bg_color,
                                self.screen_mid[0], self.GAME_ORIGIN[1])
            gg.draw_center_rect(self.screen,
                                2*self.BUFFER_DIST, self.SCREEN_HEIGHT,
                                self.bg_color,
                                self.GAME_ORIGIN[0], self.screen_mid[1])

            gg.draw_filled_aacircle(self.screen,
                                    self.START_DIST-self.cursor.RAD,
                                    self.bg_color_alt_2,
                                    self.START_COORDS[0], self.START_COORDS[1])

    def draw_indicator(self):
        if self.dof == 1:
            gg.draw_center_rect(self.screen,
                                2*self.indicator_rad, self.SCREEN_HEIGHT,
                                self.indicator_color,
                                self.START_COORDS[0], self.screen_mid[1])
        elif self.dof == 2:
            gg.draw_filled_aacircle(self.screen,
                                    self.indicator_rad,
                                    self.indicator_color,
                                    self.START_COORDS[0], self.START_COORDS[1])


    def quit(self):
        sys.exit()

if __name__ == "__main__":
    game = Trainer()
    if game.exp_type == 'timed':
        game.run_timed()
    elif game.exp_type == 'block':
        game.run_block()

