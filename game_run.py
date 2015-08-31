import numpy as np
import fileutils as fu
import game_filter as gf
import pygame
import sys

def check_in_start(game, time_passed):
    if check_in_start_rad(game): 
        game.indicator_color = game.INDICATOR_COLOR
        game.timers['reset_hold'].update(time_passed)
        game.indicator_rad = game.INDIC_RAD_MAX*(game.timers['reset_hold'].time
                                              /float(game.timers['reset_hold'].MAX_TIME))
        if game.timers['reset_hold'].time_limit_hit:
            game.indicator_color = game.INDICATOR_COLOR_2
            game.indicator_rad = game.INDIC_RAD_MAX
            game.cursor.start_ready = True
    else:
        game.indicator_rad = 0
        game.timers['reset_hold'].reset()

def cap_indicator_rad(game):
    game.indicator_rad = min(game.indicator_rad, game.INDIC_RAD_MAX)

def check_if_left(game):
    if not(check_in_start_rad(game)):
        game.indicator_color = game.INDICATOR_COLOR
        game.indicator_rad = 0
        game.cursor.has_left = True
        if game.next_target == 'new':
            game.target.set_new_target()
        else:
            game.target.reset_error_metric()
        game.timers['signal'].reset()
        game.timers['tr'].reset()

def check_in_start_rad(game):
    if game.dof == 1:
        return (abs(game.cursor.pos[0]-game.START_COORDS[0])
                <= game.START_DIST)
    elif game.dof == 2:
        return (np.linalg.norm(game.cursor.pos-game.START_COORDS)
                <= game.START_DIST)

def check_error_metric_time(game, time_passed):
    if check_error_metric(game):
        game.timers['reach_hold'].update(time_passed)
        if game.timers['reach_hold'].time_limit_hit:
            game.cursor.has_left = False
            game.cursor.start_ready = False
            game.timers['reset_hold'].reset()
            game.timers['reach_hold'].reset()
    else:
        game.timers['reach_hold'].reset()

def check_error_metric(game):
    if game.target.error_metric >= game.target.MIN_SUCCESS_SCORE:
        return True
    else:
        return False

def frame_based_updates_timed(game):
    fu.timed_frame_record(game, game.f_timed_frame)
    if game.timers['tr'].count <= game.TRS_SHOW_UPDATE_RATE:
        game.indicator_rad = game.INDIC_RAD_MAX*(game.timers['tr'].time
                                              /float(game.timers['tr'].MAX_TIME))
    else:
        game.indicator_rad = 0
    if game.timers['tr'].count == game.TRS_SHOW_UPDATE_RATE:
        i_c_1 = game.INDICATOR_COLOR[0]
        i_c_2 = game.INDICATOR_COLOR[1]
        i_c_3 = game.INDICATOR_COLOR[2]
        i_c_2 = i_c_2 - (i_c_2-i_c_3)*(game.timers['tr'].time
                                       /float(game.timers['tr'].MAX_TIME))
        game.indicator_color = i_c_1, i_c_2, i_c_3

def frame_based_updates_block(game):
    fu.block_frame_record(game, game.f_block_frame)

    if (game.playback_bool
            and game.next_feedback == 'intermittent'):
        game.playback_time_buffer[game.move_counter] = (
            game.timers['block'].time)
        game.playback_pos_buffer[0,game.move_counter] = (
            game.cursor.pos[0])
        game.playback_pos_buffer[1,game.move_counter] = (
            game.cursor.pos[1])
        game.move_counter += 1

    game.indicator_rad = int(game.INDIC_RAD_MAX*(game.timers['block'].time
                                /float(game.timers['block'].MAX_TIME)))

def signal_based_updates(game):
    game.target.error_metric_conv_sampled_buffer = np.roll(
        game.target.error_metric_conv_sampled_buffer, -1)
    game.target.error_metric_conv_sampled_buffer[-1] = (np.mean(
        game.target.error_metric_conv_buffer[-game.SAMPLE_FRAMES:])
        + game.noise_var*np.random.normal())
    game.timers['signal'].time_limit_hit = False

def trial_type_based_updates(game):
    if np.mod(game.trial_count, game.NUM_TRIALS) == 0:
        game.trial_type_count += 1
        game.trial_count = 0

    if game.trial_type_count > game.TRIAL_TYPES:
        game.quit()

    if np.mod(game.trial_type_count, 2) == 0:
        game.next_visible = False
        game.NUM_TRIALS = game.INVISIBLE_TRIALS
    else:
        game.next_visible = True
        game.NUM_TRIALS = game.VISIBLE_TRIALS

    if game.trial_type_count <= 4:
        game.next_dof = 1
    else:
        game.next_dof = 2

    if np.mod(game.trial_type_count-1, 4) < 2:
        game.next_ir = 'impulse'
    else:
        game.next_ir = 'hrf'

    game.set_trial()
        

def tr_based_updates(game):
    if (check_error_metric(game)
            and game.exp_type == 'timed'):
        game.cursor.has_left = False
        game.cursor.start_ready = False
        game.timers['reset_hold'].reset()
        fu.timed_trial_record(game, game.f_timed_trial)
        game.trial_count += 1
        trial_type_based_updates(game)
    else:
        game.target.error_metric = np.mean(
            game.target.error_metric_conv_sampled_buffer[
                -game.TRS_SAMPLES_DICT[game.tr]:])
        game.timers['tr'].time_limit_hit = False
        if game.exp_type == 'block':
            if game.block_tr_count < len(game.block_nfb_buffer):
                game.block_nfb_buffer[game.block_tr_count] = (
                    game.target.error_metric)
            game.playback_nfb_points[game.block_tr_count] = (
                game.target.error_metric)
            game.block_tr_count += 1

def block_based_updates(game):
    game.total_block_count += 1
    game.trial_block_count += 1
    game.cursor.has_left = False
    game.cursor.start_ready = False
    game.timers['reset_hold'].reset()
    game.timers['block'].reset()

    if game.playback_bool:
        # simulate the rest of desired time shifted points
        while game.timers['tr'].count < game.PLAYBACK_TRS:
            time_passed = 1000/float(game.FRAME_RATE)
            game.target.update(game.START_COORDS)
            game.timers['signal'].update(time_passed)
            game.timers['tr'].update(time_passed)
            if game.timers['signal'].time_limit_hit:
                signal_based_updates(game)
                if game.timers['tr'].time_limit_hit:
                    tr_based_updates(game)
        # filter
        # pick out time points and generate playback
        # nfb_points = np.arange(game.BLOCK_TRS)/float(game.BLOCK_TRS)
        nfb_points = game.playback_nfb_points[-game.BLOCK_TRS:]
        game.playback_nfb_buffer = gf.interp_playback_nfb(game, nfb_points)
        game.run_playback()
        game.reset_playback_buffers()

    block_score = np.mean(game.block_nfb_buffer)
    game.block_nfb_buffer = np.zeros(len(game.block_nfb_buffer))
    game.block_tr_count = 0
    game.target.error_metric = block_score
    if block_score > game.MIN_SUCCESS_SCORE:
        fu.block_trial_record(game, game.f_block_trial)
        game.therm.set_score_color('good')
        game.trial_count += 1
        game.trial_block_count = 0
        game.next_target = 'new'
        if game.next_feedback == 'continuous':
            game.next_feedback = 'intermittent'
        else:
            game.next_feedback = 'continuous'
        if np.mod(game.trial_count,2)==0:
            if game.next_noise == 'good':
                game.next_noise = 'bad'
            else:
                game.next_noise = 'good'
            game.set_noise()
    else:
        game.therm.set_score_color('bad')
        game.next_target = 'same'
    if game.trial_count >= game.NUM_BLOCK_TRIALS:
        game.quit()

