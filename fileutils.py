import os, sys
import numpy as np

#########################
# timed trial recording #
#########################

def write_all_headers_timed(game):
    if os.path.exists(game.subj_dir):
        pass
    else:
        os.mkdir(game.subj_dir)
    game.f_timed_frame = open(game.subj_dir
                              + '/timed_frame_'
                              + game.subj_id
                              + '.txt','w')
    game.f_timed_trial = open(game.subj_dir
                              + '/timed_trial_'
                              + game.subj_id
                              + '.txt','w')
    timed_frame_header(game.f_timed_frame)
    timed_trial_header(game.f_timed_trial)

def timed_frame_header(f):
    f.write('{trial_number},'
            '{trial_time},'
            '{dof},'
            '{hrf},'
            '{visible},'
            '{nfb_score},'
            '{cursor_xpos},'
            '{cursor_ypos},'
            '{target_xpos},'
            '{target_ypos}\n'.format(trial_number='trial_number',
                              trial_time='trial_time',
                              dof='dof',
                              hrf='hrf',
                              visible='visible',
                              nfb_score='nfb_score',
                              cursor_xpos='cursor_xpos',
                              cursor_ypos='cursor_ypos',
                              target_xpos='target_xpos',
                              target_ypos='target_ypos'))

def timed_frame_record(game, f):
    cursor_xpos = abs(game.START_COORDS[0]
                      -game.cursor.pos[0])
    target_xpos = abs(game.START_COORDS[0]
                      -game.target.pos[0])
    if game.dof == 2:
        cursor_ypos = abs(game.START_COORDS[1]
                          -game.cursor.pos[1])
        target_ypos = abs(game.START_COORDS[1]
                          -game.target.pos[1])
    else:
        cursor_ypos = 0
        target_ypos = 0
    f.write('{trial_number},'
            '{trial_time},'
            '{dof},'
            '{hrf},'
            '{visible},'
            '{nfb_score},'
            '{cursor_xpos},'
            '{cursor_ypos},'
            '{target_xpos},'
            '{target_ypos}\n'.format(trial_number=str(game.trial_count),
                              trial_time=str(float(game.timers['tr'].time
                                                   + game.timers['tr'].count
                                                    *game.timers['tr'].MAX_TIME)
                                              /1000),
                              dof=str(game.dof),
                              hrf=str(game.target.fb_mode),
                              visible=str(game.training_mode),
                              nfb_score=str(game.target.error_metric),
                              cursor_xpos=str(cursor_xpos),
                              cursor_ypos=str(cursor_ypos),
                              target_xpos=str(target_xpos),
                              target_ypos=str(target_ypos)))


def timed_trial_header(f):
    f.write('{time},'
            '{dof},'
            '{hrf},'
            '{visible},'
            '{xpos},'
            '{ypos}\n'.format(time='trs_to_target',
                              dof='dof',
                              hrf='hrf',
                              visible='visible',
                              xpos='target_xpos',
                              ypos='target_ypos'))

def timed_trial_record(game, f):
    target_xpos = abs(game.START_COORDS[0]
                      -game.target.pos[0])
    if game.dof == 2:
        target_ypos = abs(game.START_COORDS[1]
                          -game.target.pos[1])
    else:
        target_ypos = 0
    f.write('{time},'
            '{dof},'
            '{hrf},'
            '{visible},'
            '{xpos},'
            '{ypos}\n'.format(time=str(game.timers['tr'].count),
                                 dof=str(game.dof),
                                 hrf=str(game.target.fb_mode),
                                 visible=str(game.training_mode),
                                 xpos=str(target_xpos),
                                 ypos=str(target_ypos)))

#########################
# block trial recording #
#########################

def write_all_headers_block(game):
    if os.path.exists(game.subj_dir):
        pass
    else:
        os.mkdir(game.subj_dir)
    game.f_block_frame = open(game.subj_dir
                              + '/block_frame_'
                              + game.subj_id
                              + '.txt','w')
    game.f_block_trial = open(game.subj_dir
                              + '/block_trial_'
                              + game.subj_id
                              + '.txt','w')
    block_frame_header(game.f_block_frame)
    block_trial_header(game.f_block_trial)

def block_frame_header(f):
    f.write('{trial_number},'
            '{block_number},'
            '{trial_time},'
            '{feedback},'
            '{noise},'
            '{nfb_score},'
            '{cursor_xpos},'
            '{cursor_ypos},'
            '{target_xpos},'
            '{target_ypos}\n'.format(trial_number='trial_number',
                              block_number='block_number',
                              trial_time='trial_time',
                              feedback='feedback',
                              noise='noise',
                              nfb_score='nfb_score',
                              cursor_xpos='cursor_xpos',
                              cursor_ypos='cursor_ypos',
                              target_xpos='target_xpos',
                              target_ypos='target_ypos'))

def block_frame_record(game, f):
    cursor_xpos = abs(game.START_COORDS[0]
                      -game.cursor.pos[0])
    target_xpos = abs(game.START_COORDS[0]
                      -game.target.pos[0])
    if game.dof == 2:
        cursor_ypos = abs(game.START_COORDS[1]
                          -game.cursor.pos[1])
        target_ypos = abs(game.START_COORDS[1]
                          -game.target.pos[1])
    else:
        cursor_ypos = 0
        target_ypos = 0
    f.write('{trial_number},'
            '{block_number},'
            '{trial_time},'
            '{feedback},'
            '{noise},'
            '{nfb_score},'
            '{cursor_xpos},'
            '{cursor_ypos},'
            '{target_xpos},'
            '{target_ypos}\n'.format(trial_number=str(game.trial_count),
                              block_number=str(game.trial_block_count),
                              trial_time=str(float(game.timers['tr'].time
                                                   + game.timers['tr'].count
                                                    *game.timers['tr'].MAX_TIME)
                                              /1000),
                              feedback=game.next_feedback,
                              noise=game.next_noise,
                              nfb_score=str(game.target.error_metric),
                              cursor_xpos=str(cursor_xpos),
                              cursor_ypos=str(cursor_ypos),
                              target_xpos=str(target_xpos),
                              target_ypos=str(target_ypos)))


def block_trial_header(f):
    f.write('{time},'
            '{feedback},'
            '{noise},'
            '{xpos},'
            '{ypos}\n'.format(time='blocks_to_target',
                              feedback='feedback',
                              noise='noise',
                              xpos='target_xpos',
                              ypos='target_ypos'))

def block_trial_record(game, f):
    target_xpos = abs(game.START_COORDS[0]
                      -game.target.pos[0])
    if game.dof == 2:
        target_ypos = abs(game.START_COORDS[1]
                          -game.target.pos[1])
    else:
        target_ypos = 0
    f.write('{time},'
            '{feedback},'
            '{noise},'
            '{xpos},'
            '{ypos}\n'.format(time=game.trial_block_count,
                              feedback=game.next_feedback,
                              noise=game.next_noise,
                              xpos=str(target_xpos),
                              ypos=str(target_ypos)))


##########################################
# template file recording functions here #
##########################################

def sample_header(f):
    f.write('{key1},'
            '{key2},'
            '{keyn}\n'.format(key1='key1',
                              key2='key2',
                              keyn='keyn'))

def sample_record(game, f):
    f.write('{key1},'
            '{key2},'
            '{keyn}\n'.format(key1=game.val_1,
                              key2=game.val_2,
                              keyn=game.val_n))

