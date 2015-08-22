import os, sys
import numpy as np

def write_all_headers(game):
    if os.path.exists(game.subj_dir):
        pass
    else:
        os.mkdir(game.subj_dir)

    game.f_timed_trial = open(game.subj_dir
                              + '/timed_trial_'
                              + game.subj_id
                              + '.txt','w')

    timed_trial_header(game.f_timed_trial)

########################################
# actual file recording functions here #
########################################

def timed_trial_header(f):
    f.write('{time},'
            '{dof},'
            '{hrf},'
            '{visible},'
            '{xpos},'
            '{ypos}\n'.format(time='time',
                                 dof='dof',
                                 hrf='hrf',
                                 visible='visible',
                                 xpos='xpos',
                                 ypos='ypos'))

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

