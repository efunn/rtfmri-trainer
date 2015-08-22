import pygame
import numpy as np
import ctypes
import time
import os
import ni_consts as c
import game_filter as gf

#######################################
# generic driver and datatype imports #
#######################################

NIDAQ = ctypes.windll.nicaiu
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
MINIMUM = float64(0)
MAXIMUM = float64(5)

class Pydaq(object):

    def __init__(self,
                 dev_name='Dev1/ai0:1',
                 frame_rate=120,
                 lp_filt_freq=4,
                 lp_filt_order=3,
                 force_params='force_params.txt'):

        # specific variables for this device to operate with
        self.load_force_params(force_params)
        self.dev_name = dev_name
        self.task_handle = uInt32 
        self.ai_task_handle = self.task_handle(0)
        self.num_channels = 2
        self.points = 1
        self.points_read = uInt32()
        self.DAQ_data = np.zeros((self.points*self.num_channels), dtype=np.float64)

        NIDAQ.DAQmxCreateTask("", ctypes.byref(self.ai_task_handle))
        NIDAQ.DAQmxCreateAIVoltageChan(self.ai_task_handle, self.dev_name, '',
                                           c.DAQmx_Val_Diff, MINIMUM, MAXIMUM,
                                           c.DAQmx_Val_Volts, None)
        NIDAQ.DAQmxStartTask(self.ai_task_handle)   

        # define data buffers and filters

        self.volts_zero = np.array([0.0,0.0])
        self.frame_rate = frame_rate
        self.zero_time = int(0.25*frame_rate)
        self.buffer_size = 3*frame_rate
        self.volts_buffer = np.zeros((2, self.buffer_size))
        self.force_buffer = np.zeros((2, self.buffer_size))
        (self.butter_lowpass_rt_b,
         self.butter_lowpass_rt_a) = gf.butter_lowpass(lp_filt_freq,
                                                       self.frame_rate,
                                                       lp_filt_order)


    def get_force(self):
        new_volts_in = self.filt_volts(self.get_volts())
        new_force_in = self.force_transform(new_volts_in-self.volts_zero)
        return new_force_in


    def get_volts(self):
        NIDAQ.DAQmxReadAnalogF64(self.ai_task_handle, uInt32(int(self.points)),
                                 float64(10.0),
                                 c.DAQmx_Val_GroupByChannel,
                                 self.DAQ_data.ctypes.data, 100,
                                 ctypes.byref(self.points_read), None)	
        return self.DAQ_data[0], self.DAQ_data[1]


    def load_force_params(self, f='force_params.txt'):
        self.force_params = np.loadtxt(f)


    def force_transform(self, force_in):
        f_x = self.force_interp(force_in[0], 0)
        f_y = self.force_interp(force_in[1], 1)
        self.force_buffer = np.roll(self.force_buffer, -1) 
        self.force_buffer[:,-1] = f_x, f_y
        return f_x, f_y


    def force_interp(self, force_in, axis):
        axis = 2*axis
        if force_in >= self.force_params[axis,-1]:
            force_out = self.force_params[axis+1,-1]
        elif force_in <= self.force_params[axis,0]:
            force_out = self.force_params[axis+1,0]
        else:
            idx = np.argmax(self.force_params[axis,:] > force_in) - 1
            force_out = (self.force_params[axis+1,idx]
                         + (self.force_params[axis+1,idx+1]-self.force_params[axis+1,idx])
                         /(self.force_params[axis,idx+1]-self.force_params[axis,idx])
                         *(force_in-self.force_params[axis,idx]))
        return force_out


    def filt_volts(self, volts_in):
        self.volts_buffer = np.roll(self.volts_buffer, -1) 
        self.volts_buffer[:,-1] = volts_in[0], volts_in[1] 
        v_x = gf.filter_data_rt(self.volts_buffer[0,:],
                                self.butter_lowpass_rt_b,
                                self.butter_lowpass_rt_a)
        v_y = gf.filter_data_rt(self.volts_buffer[1,:],
                                self.butter_lowpass_rt_b,
                                self.butter_lowpass_rt_a)
        return v_x, v_y


    def set_volts_zero(self):
        self.volts_zero[0] = np.mean(self.volts_buffer[0,-self.zero_time:-1])
        self.volts_zero[1] = np.mean(self.volts_buffer[1,-self.zero_time:-1])

